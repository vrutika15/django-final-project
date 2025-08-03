from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from datetime import datetime
from .models import Project
from .forms import ProjectForm
from resources.models import Resource


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
    return render(request, 'home.html', {
        'years': years,
        'months': months,
        'year': year,
        'month': month,
        'projects': projects,
        'resources': resources,
        'current_year': now.year,
        'current_month': now.month,
    })

def project_list(request):
    years = list(Project.objects.values_list('year', flat=True).distinct())
    months = list(Project.objects.values_list('month', flat=True).distinct())
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    projects = Project.objects.all()
    if selected_year:
        projects = projects.filter(year=selected_year)
    if selected_month:
        projects = projects.filter(month=selected_month)
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
        project.delete()
        return redirect('projects:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project':project})


def attendance_home(request):
    resources = Resource.objects.all()
    projects = Project.objects.prefetch_related('resources').all()

    # Totals for resource
    total_working_days = sum(r.working_days for r in resources)
    total_present_days = sum(r.present_day for r in resources)
    total_present_hours = sum(r.present_hours for r in resources)
    presence_percentage = (100 * total_present_days)/total_working_days if total_working_days else 0

    # Totals for project
    total_billable_days = sum(p.billable_days for p in projects)
    total_non_billable_days = sum(p.non_billable_days for p in projects)
    total_billable_hours = sum(p.billable_hours for p in projects)
    total_non_billable_hours = sum(p.non_billable_hours for p in projects)

    # team productivity perc
    if total_present_hours > 0:
        team_productivity_percentage = (100 * total_billable_hours) / total_present_hours
    else:
        team_productivity_percentage = 0


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
        'presence_percentage' : presence_percentage,
        'team_productivity_percentage' : team_productivity_percentage
    }

    return render(request, 'attendance/attendance_home.html', context)