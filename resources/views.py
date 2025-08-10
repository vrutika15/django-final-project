from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource
from .forms import ResourceForm
from django.contrib import messages
from calendar import month_name
from projects.models import Project
from interns.models import Intern
 
def resource_list(request):
    resources = Resource.objects.all()

    year = request.GET.get("year")
    month = request.GET.get("month")

    if year:
        resources = resources.filter(year=year)
    if month:
        resources = resources.filter(month=month)

    #distinct years for dropdown
    years = Resource.objects.values_list('year', flat=True).distinct().order_by('-year')
    #month name in whole name format
    months = [(i, month_name[i]) for i in range(1, 13)]

    return render(request, "resources/resource_list.html", {
        "resources": resources,
        "years": years,
        "months": months,
    })

    
def resource_create(request):
    # Get year/month from session (set by dashboard)
    year = request.session.get('selected_year')
    month = request.session.get('selected_month')
    if not (year and month):
        messages.warning(request, 'Please select year and month from dashboard before adding a resource.')
        return redirect('home')
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            #Set the year and month manually from session
            resource.year = year
            resource.month = month
            resource.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm()
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Add Resource', 'year': year, 'month': month})
 
 
def resource_update(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resources:resource_list')
    else:
        #pre-fill form with existing resource data, if get reques
        form = ResourceForm(instance=resource)
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Edit Resource'})

#func for deactivating a resource instead of deleting
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        #check if this resource is referenced by any project
        if resource.profiled_projects.exists() or resource.assigned_projects.exists():
            messages.error(
                request,
                "Cannot deactivate this resource because it's used in one or more projects."
            )
        else:
            resource.is_active = False
            resource.save()
            messages.success(request, f"Resource '{resource.resource_name}' has been deactivated.")
        return redirect('resources:resource_list')

    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})

def dashboard(request):
    resource = Resource.objects.all()
    project = Project.objects.all()
    intern = Intern.objects.all()

    resource_count = Resource.objects.values('resource_name').count()
    project_count = Project.objects.values('project_name').count()
    intern_count = Intern.objects.values('name').count()

     #team prouctivity percentage 
    total_present_hours = sum(r.present_hours for r in resource)
    total_billable_hours = sum(p.billable_hours for p in project)
    team_productivity_percentage = (100 * total_billable_hours / total_present_hours) if total_present_hours > 0 else 0

    # presence percentage
    total_present_days = sum(r.present_day for r in resource)
    total_working_days = sum(r.working_days for r in resource)
    presence_percentage = (100 * total_present_days)/total_working_days if total_working_days else 0

    context = {
        'resource': resource,
        'project': project,
        'intern': intern,
        'resource_count': resource_count,
        'project_count': project_count,
        'intern_count': intern_count,
        'total_present_hours': total_present_hours,
        'total_billable_hours': total_billable_hours,
        'team_productivity_percentage': team_productivity_percentage,
        'total_present_days': total_present_days,
        'total_working_days': total_working_days,
        'presence_percentage': presence_percentage
    }
    return render(request,'admin_dashboard.html',context)
