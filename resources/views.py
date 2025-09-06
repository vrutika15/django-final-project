from datetime import date, timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource, ResourceMonthlyData
from .forms import ResourceGlobalForm, ResourceMonthlyForm
from django.contrib import messages
from calendar import calendar, month_name
from projects.models import Project
from interns.models import Intern
from django.db.models import Sum, Q
from projects.models import Project,ProjectReport
from interns.models import Intern
import calendar
from django.utils import timezone
from django.http import HttpResponseForbidden

def resource_list(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    resources = Resource.objects.all()

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    context={
        "resources": resources,
        "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
    }
    
    return render(request, "resources/resource_list.html", context)


def resource_create(request):
    if request.method == 'POST':
        form = ResourceGlobalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceGlobalForm()
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Add Resource'})


def resource_update(request, pk):
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceGlobalForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceGlobalForm(instance=resource)
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Edit Resource'})


def resource_delete(request, pk):
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        if resource.profiled_projects.exists() or resource.assigned_projects.exists():
            messages.error(request, "Cannot deactivate this resource because it's used in one or more projects.")
        else:
            resource.is_active = False
            resource.save()
            messages.success(request, f"Resource '{resource.resource_name}' has been deactivated.")
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})


def monthly_data_create(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)

    if request.method == 'POST':
        form = ResourceMonthlyForm(request.POST)
        if form.is_valid():
            monthly_data = form.save(commit=False)
            monthly_data.resource = resource
            monthly_data.save()
            messages.success(request, f"Monthly data for {resource.resource_name} created successfully.")
            return redirect('resources:resource_list')
    else:
        form = ResourceMonthlyForm()

    return render(request, 'resources/monthly_data_form.html', {
        'form': form,
        'resource': resource,
        'title': f"Add Monthly Data for {resource.resource_name}"
    })


def monthly_data_update(request, pk):
    role = request.session.get('role')
    if role not in ['user', 'admin']:
        return HttpResponseForbidden("Not allowed")
    monthly_data = get_object_or_404(ResourceMonthlyData, pk=pk)

    if request.method == 'POST':
        form = ResourceMonthlyForm(request.POST, instance=monthly_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Monthly data updated successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceMonthlyForm(instance=monthly_data)

    return render(request, 'resources/monthly_data_form.html', {
        'form': form,
        'resource': monthly_data.resource,
        'title': f"Edit Monthly Data for {monthly_data.resource.resource_name}"
    })


def dashboard(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    resourceAttendance = ResourceMonthlyData.objects.filter(
        year=selected_year, month=selected_month
    )
    projectAttendance = ProjectReport.objects.filter(
        year=selected_year, month=selected_month
    )

    # total counts
    resources = Resource.objects.filter(is_active=True).count()
    projects = Project.objects.filter(is_active=True).count()
    interns = Intern.objects.count()

    # charts
    total_present_day = sum(r.present_day for r in resourceAttendance)
    total_working_days = sum(r.working_days for r in resourceAttendance)
    presence_percentage = (100*total_present_day)/total_working_days if total_working_days else 0

    total_present_hours = sum(r.present_hours for r in resourceAttendance)
    total_billable_hours = sum(p.billable_hours for p in projectAttendance)
    team_productivity_percentage = (100*total_billable_hours)/total_present_hours if total_present_hours else 0

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    context = {
        "resources": resources,
        "projects": projects,
        "interns": interns,
        "total_present_day": total_present_day,
        "total_working_days": total_working_days,
        "presence_percentage": presence_percentage,
        "total_present_hours": total_present_hours,
        "total_billable_hours": total_billable_hours,
        "team_productivity_percentage": team_productivity_percentage,
        "resourceAttendance": resourceAttendance,
        "projectAttendance": projectAttendance,
        "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
    }
    return render(request,'admin_dashboard.html',context)
