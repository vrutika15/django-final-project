from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from datetime import datetime
from .models import Project
from .forms import ProjectForm
from resources.models import Resource
from django.db.models import ProtectedError,Prefetch
from django.contrib import messages


def team_dashboard_redirect(request):
    return redirect('dashboard_home')


def dashboard_home(request):
    years = list(range(2020, 2031))
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    # Get year and month from GET params, fallback to current year/month
    now = datetime.now()
    tab = request.GET.get('tab', 'projects') #default to projects tab
    year_param = request.GET.get('year')
    month_param = request.GET.get('month')
    try:
        year = int(year_param) if year_param else now.year
    except ValueError:
        year = now.year
    try:
        month = int(month_param) if month_param else now.month
    except ValueError:
        month = now.month
    # Store in session for resource creation
    if year_param and month_param:
        request.session['selected_year'] = year
        request.session['selected_month'] = month
    # Filter projects/resources by year and month (month as number)
    from resources.models import Resource
    from .models import Project
    projects = Project.objects.filter(year=year, month=month)
    resources = Resource.objects.filter(year=year, month=month)

    #team productivity percentage
    team_productivity_percentage = None
    # Default values
    total_working_days = 0
    total_present_days = 0
    total_present_hours = 0
    presence_percentage = 0

    total_billable_days = 0
    total_non_billable_days = 0
    total_billable_hours = 0
    total_non_billable_hours = 0
    if tab == 'charts':
        #team prouctivity percentage 
        total_present_hours = sum(r.present_hours for r in resources)
        total_billable_hours = sum(p.billable_hours for p in projects)
        team_productivity_percentage = (100 * total_billable_hours / total_present_hours) if total_present_hours > 0 else 0

        # presence percentage
        total_present_days = sum(r.present_day for r in resources)
        total_working_days = sum(r.working_days for r in resources)
        presence_percentage = (100 * total_present_days)/total_working_days if total_working_days else 0

     # Totals for resource
    if tab == 'resources':   
       total_working_days = sum(r.working_days for r in resources)
       total_present_days = sum(r.present_day for r in resources)
       total_present_hours = sum(r.present_hours for r in resources)
       presence_percentage = (100 * total_present_days)/total_working_days if total_working_days else 0

    # Totals for project
    if tab  == 'projects':
        total_present_days = sum(p.present_day for p in projects)
        total_billable_days = sum(p.billable_days for p in projects)
        total_non_billable_days = sum(p.non_billable_days for p in projects)
        total_billable_hours = sum(p.billable_hours for p in projects)
        total_non_billable_hours = sum(p.non_billable_hours for p in projects)

    return render(request, 'home.html', {
        'years': years,
        'months': months,
        'year': year,
        'month': month,
        'projects': projects,
        'resources': resources,
       # 'active_tab': active_tab,
        'current_year': now.year,
        'current_month': now.month,
        'active_tab': tab,
        'team_productivity_percentage': team_productivity_percentage,
        'total_working_days': total_working_days,
        'total_present_days': total_present_days,
        'total_present_hours': total_present_hours,
        'presence_percentage' : presence_percentage,
        'total_billable_days': total_billable_days,
        'total_non_billable_days': total_non_billable_days,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
    })

def project_list(request):
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    projects = Project.objects.all()

    if selected_year:
        projects = projects.filter(year=selected_year)
    if selected_month:
        projects = projects.filter(month=selected_month)

    #get distinct years and months for filters
    years = Project.objects.values_list('year', flat=True).distinct().order_by('year')
    months = Project.objects.values_list('month', flat=True).distinct().order_by('month')

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    })


def project_create(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project_form.save()
            return redirect('projects:project_list')
    else:
        year = request.session.get('selected_year')
        month = request.session.get('selected_month')
        project_form = ProjectForm(initial={'year': year, 'month': month})

    return render(request, 'projects/project_form.html', {
        'form': project_form,
        'title': 'Create Project'
    })


def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, instance=project)
        if project_form.is_valid():
            project_form.save()
            return redirect('projects:project_list')
    else:
        project_form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {
        'form': project_form,
        'title': 'Edit Project'
    })

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.is_active = False
        project.save()
        messages.success(request, f"Project '{project.project_name}' was marked as inactive.")
        return redirect('projects:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})


def attendance_home(request):
    resources = Resource.objects.all()
    projects = Project.objects.prefetch_related('resources').all()

    # Totals for resource
    total_working_days = sum(r.working_days for r in resources)
    total_present_days = sum(r.present_day for r in resources)
    total_present_hours = sum(r.present_hours for r in resources)
    presence_percentage = (100 * total_present_days)/total_working_days if total_working_days else 0

    # Totals for project
    total_present_days = sum(p.present_day for p in projects)
    total_billable_days = sum(p.billable_days for p in projects)
    total_non_billable_days = sum(p.non_billable_days for p in projects)
    total_billable_hours = sum(p.billable_hours for p in projects)
    total_non_billable_hours = sum(p.non_billable_hours for p in projects)

    context = {
        'resources': resources,
        'projects': projects,
        'total_working_days': total_working_days,
        'total_present_days': total_present_days,
        'total_present_hours': total_present_hours,
        'total_billable_days': total_billable_days,
        'total_non_billable_days': total_non_billable_days,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
        'presence_percentage' : presence_percentage
    }

    return render(request, 'attendance/attendance_home.html', context)

def tree_structure_view(request):
    """
    Display a project list on the left and detailed project structure on the right.
    """
    # Get all projects with their resources prefetched for efficiency
    projects = Project.objects.prefetch_related('resources', 'project_profile', 'poc').filter(is_active=True).order_by('project_name')
   
    # Get all resources for reference
    resources = Resource.objects.filter(is_active=True).order_by('resource_name')
   
    # Get selected project from URL parameter
    selected_project_id = request.GET.get('project')
    selected_project = None
   
    if selected_project_id:
        try:
            selected_project = Project.objects.prefetch_related('resources', 'project_profile', 'poc').get(id=selected_project_id, is_active=True)
        except Project.DoesNotExist:
            selected_project = None
   
    # If no project is selected, select the first one
    if not selected_project and projects.exists():
        selected_project = projects.first()
   
    # Group projects by year and month for the left sidebar
    projects_by_period = {}
    for project in projects:
        period_key = f"{project.year}-{project.month:02d}"
        if period_key not in projects_by_period:
            projects_by_period[period_key] = {
                'year': project.year,
                'month': project.month,
                'month_name': project.get_month_display(),
                'projects': []
            }
        projects_by_period[period_key]['projects'].append(project)
   
    # Sort periods chronologically
    sorted_periods = sorted(projects_by_period.keys(), reverse=True)
 
    #resorces
    resources = Resource.objects.filter(is_active=True).order_by('-year', '-month', 'resource_name')
    selected_resource_id = request.GET.get('resource')
    selected_resource = None
 
    if selected_resource_id:
        try:
             """selected_resource = Resource.objects.prefetch_related(
            Prefetch('assigned_projects', queryset=Project.objects.select_related('project_profile').prefetch_related('resources'))
        ).get(id=selected_resource_id, is_active=True)"""
             selected_resource = Resource.objects.prefetch_related(
    Prefetch(
        'assigned_projects',
        queryset=Project.objects.prefetch_related('project_profile', 'resources', 'poc')
    )
).get(id=selected_resource_id, is_active=True)
 
        except Resource.DoesNotExist:
            selected_resource = None
 
    if not selected_resource and resources.exists():
        selected_resource = resources.first()
 
    # Group resources by year and month
    resources_by_period = {}
    for resource in resources:
        period_key = f"{resource.year}-{resource.month:02d}"
        if period_key not in resources_by_period:
            resources_by_period[period_key] = {
                'year': resource.year,
                'month': resource.month,
                'month_name': resource.get_month_display(),
                'resources': []
            }
        resources_by_period[period_key]['resources'].append(resource)
 
    sorted_resource_periods = sorted(resources_by_period.keys(), reverse=True)
 
   
    # Calculate summary statistics
    total_projects = projects.count()
    total_resources = resources.count()
    total_billable_hours = sum(p.billable_hours for p in projects)
    total_non_billable_hours = sum(p.non_billable_hours for p in projects)
    total_hours = total_billable_hours + total_non_billable_hours
   
    context = {
        #projects
        'projects_by_period': projects_by_period,
        'sorted_periods': sorted_periods,
        'selected_project': selected_project,
 
        #resorces
        'resources_by_period': resources_by_period,
        'sorted_resource_periods': sorted_resource_periods,
        'selected_resource': selected_resource,
 
        #stats
        'total_projects': total_projects,
        'total_resources': total_resources,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
        'total_hours': total_hours,
    }
   
    return render(request, 'projects/tree_structure.html', context)
 

#to add the resources to the tree view structure
"""
def tree_structure_view(request):
    
    Display a project list on the left and detailed project structure on the right.
    
    # Get all projects with their resources prefetched for efficiency
    projects = Project.objects.prefetch_related('resources', 'project_profile').filter(is_active=True).order_by('project_name')
    
    # Get all resources for reference
    resources = Resource.objects.filter(is_active=True).order_by('resource_name')
    
    # Get selected project from URL parameter
    selected_project_id = request.GET.get('project')
    selected_project = None
    
    if selected_project_id:
        try:
            selected_project = Project.objects.prefetch_related('resources', 'project_profile').get(id=selected_project_id, is_active=True)
        except Project.DoesNotExist:
            selected_project = None
    
    # If no project is selected, select the first one
    if not selected_project and projects.exists():
        selected_project = projects.first()
    
    # Group projects by year and month for the left sidebar
    projects_by_period = {}
    for project in projects:
        period_key = f"{project.year}-{project.month:02d}"
        if period_key not in projects_by_period:
            projects_by_period[period_key] = {
                'year': project.year,
                'month': project.month,
                'month_name': project.get_month_display(),
                'projects': []
            }
        projects_by_period[period_key]['projects'].append(project)
    
    # Group resources by year and month (new logic)
    resources_by_period = {}
    for resource in resources:
        period_key = f"{resource.year}-{resource.month:02d}"
        if period_key not in resources_by_period:
            resources_by_period[period_key] = {
                'year': resource.year,
                'month': resource.month,
                'month_name': resource.get_month_display(),
                'resources': []
            }
        resources_by_period[period_key]['resources'].append(resource)
    
    # Sort periods chronologically
    sorted_periods = sorted(projects_by_period.keys(), reverse=True)
    sorted_resource_periods = sorted(resources_by_period.keys(), reverse=True)
    
    # Calculate summary statistics
    total_projects = projects.count()
    total_resources = resources.count()
    total_billable_hours = sum(p.billable_hours for p in projects)
    total_non_billable_hours = sum(p.non_billable_hours for p in projects)
    total_hours = total_billable_hours + total_non_billable_hours
    
    context = {
        'projects_by_period': projects_by_period,
        'sorted_periods': sorted_periods,
        'selected_project': selected_project,
        'total_projects': total_projects,
        'total_resources': total_resources,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
        'total_hours': total_hours,
        'utilization_percentage': (total_billable_hours / total_hours * 100) if total_hours > 0 else 0,

        #new resource grouping context
        'resources_by_period': resources_by_period,
        'sorted_resource_periods': sorted_resource_periods,
    }
    
    return render(request, 'projects/tree_structure.html', context)
"""