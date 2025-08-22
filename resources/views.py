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

def resource_list(request):
    # year = request.GET.get("year")
    # month = request.GET.get("month")

    # monthly_qs = ResourceMonthlyData.objects.select_related('resource')
    # if year:
    #     monthly_qs = monthly_qs.filter(year=year)
    # if month:
    #     monthly_qs = monthly_qs.filter(month=month)

    # years = ResourceMonthlyData.objects.values_list('year', flat=True).distinct().order_by('-year')
    # months = [(i, month_name[i]) for i in range(1, 13)]

    # context = {
    #     "monthly_data": monthly_qs,
    #     "years": years,
    #     "months": months,
    #     "selected_year": year,
    #     "selected_month": month,
    # }

    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))
    year = request.GET.get("year")
    month = request.GET.get("month")

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
    """
    Create new Resource and optionally a ResourceMonthlyData record.
    For simplicity, start with only Resource creation.
    """
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
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        # Assuming you have proper related names on Project model
        if resource.profiled_projects.exists() or resource.assigned_projects.exists():
            messages.error(request, "Cannot deactivate this resource because it's used in one or more projects.")
        else:
            resource.is_active = False
            resource.save()
            messages.success(request, f"Resource '{resource.resource_name}' has been deactivated.")
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})


def monthly_data_create(request, resource_id):
    """
    Create monthly data for a given resource.
    """
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


# def dashboard(request):

#     year = int(request.GET.get('year', date.today().year))
#     month = int(request.GET.get('month', date.today().month))

#     # Aggregate monthly data for active resources
#     active_resources = Resource.objects.filter(is_active=True)

#     # Aggregate sums for present hours and working days across all monthly data for active resources
#     monthly_data_qs = ResourceMonthlyData.objects.filter(resource__in=active_resources,year=year,month=month)

#     total_present_hours = monthly_data_qs.aggregate(total=Sum('present_hours'))['total'] or 0
#     total_working_days = monthly_data_qs.aggregate(total=Sum('working_days'))['total'] or 0
#     total_present_days = monthly_data_qs.aggregate(total=Sum('present_day'))['total'] or 0

#     # Assuming Project model has billable_hours field
#     projects = Project.objects.all()
#     total_billable_hours = projects.aggregate(total=Sum('billable_hours'))['total'] or 0

#     resource_count = active_resources.count()
#     project_count = projects.count()
#     intern_count = Intern.objects.count()

#     team_productivity_percentage = (100 * total_billable_hours / total_present_hours) if total_present_hours > 0 else 0
#     presence_percentage = (100 * total_present_days / total_working_days) if total_working_days > 0 else 0

#     context = {
#         'resource_count': resource_count,
#         'project_count': project_count,
#         'intern_count': intern_count,
#         'total_present_hours': total_present_hours,
#         'total_billable_hours': total_billable_hours,
#         'team_productivity_percentage': team_productivity_percentage,
#         'total_present_days': total_present_days,
#         'total_working_days': total_working_days,
#         'presence_percentage': presence_percentage,
#         'monthly_data': monthly_data_qs,
#         'year': year,
#         'month': month,
#     }
#     return render(request, 'admin_dashboard.html', context)
from django.utils import timezone
def dashboard(request):
    # get selected year/month from query params (default = current)
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    # filter attendance by selected year and month
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

    # year and month lists
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
