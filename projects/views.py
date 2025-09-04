from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from datetime import datetime
from .models import Project, ProjectReport
from .forms import ProjectForm
from resources.models import Resource, ResourceMonthlyData
from django.db.models import Prefetch, Max, Q
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from django.utils import timezone
from datetime import datetime
import calendar
from resources.forms import ResourceMonthlyForm
from projects.forms import ProjectReportForm

# def dashboard_home(request):
#     years = list(range(2020, 2031))
#     months = [
#         'January', 'February', 'March', 'April', 'May', 'June',
#         'July', 'August', 'September', 'October', 'November', 'December'
#     ]
#     now = datetime.now()
#     tab = request.GET.get('tab', 'projects')
#     year_param = request.GET.get('year')
#     month_param = request.GET.get('month')

#     try:
#         year = int(year_param) if year_param else now.year
#     except ValueError:
#         year = now.year
#     try:
#         month = int(month_param) if month_param else now.month
#     except ValueError:
#         month = now.month

#     if year_param and month_param:
#         request.session['selected_year'] = year
#         request.session['selected_month'] = month

#     # Filter ProjectReports instead of Project
#     reports = ProjectReport.objects.filter(year=year, month=month)
#     resources = Resource.objects.filter(join_date__year=year, join_date__month=month)

#     team_productivity_percentage = None
#     total_working_days = 0
#     total_present_days = 0
#     total_present_hours = 0
#     presence_percentage = 0
#     total_billable_days = 0
#     total_non_billable_days = 0
#     total_billable_hours = 0
#     total_non_billable_hours = 0
#     resource_status = []

#     if tab == 'charts':
#         monthly_data_qs = ResourceMonthlyData.objects.filter(
#             resource__in=resources,
#             year=year,
#             month=month
#         )
#         total_present_hours = monthly_data_qs.aggregate(total=Sum('present_hours'))['total'] or 0
#         total_billable_hours = reports.aggregate(total=Sum('billable_hours'))['total'] or 0
#         team_productivity_percentage = (100 * total_billable_hours / total_present_hours) if total_present_hours > 0 else 0

#         total_present_days = monthly_data_qs.aggregate(total=Sum('present_day'))['total'] or 0
#         total_working_days = monthly_data_qs.aggregate(total=Sum('working_days'))['total'] or 0
#         presence_percentage = (100 * total_present_days) / total_working_days if total_working_days else 0

#     if tab == 'resources':
#         monthly_data_qs = ResourceMonthlyData.objects.filter(
#             resource__in=resources,
#             year=year,
#             month=month
#         )
#         total_working_days = monthly_data_qs.aggregate(total=Sum('working_days'))['total'] or 0
#         total_present_days = monthly_data_qs.aggregate(total=Sum('present_day'))['total'] or 0
#         total_present_hours = monthly_data_qs.aggregate(total=Sum('present_hours'))['total'] or 0
#         presence_percentage = (100 * total_present_days) / total_working_days if total_working_days else 0

#     if tab == 'projects':
#         total_present_days = reports.aggregate(total=Sum('present_day'))['total'] or 0
#         total_billable_days = reports.aggregate(total=Sum('billable_days'))['total'] or 0
#         total_non_billable_days = reports.aggregate(total=Sum('non_billable_days'))['total'] or 0
#         total_billable_hours = reports.aggregate(total=Sum('billable_hours'))['total'] or 0
#         total_non_billable_hours = reports.aggregate(total=Sum('non_billable_hours'))['total'] or 0

#     if tab == 'resourcesmanagement':
#         for resource in resources:
#             poc_projects = resource.poc_projects.all()
#             assigned_projects = resource.assigned_projects.all()
#             all_projects = (poc_projects | assigned_projects).distinct()

#             total_poc_count = 0
#             total_dev_count = 0

#             for project in all_projects:
#                 if resource in project.poc.all():
#                     total_poc_count += 1
#                 if resource in project.resources.all():
#                     total_dev_count += 1

#             if total_poc_count >= 5 and total_dev_count == 0:
#                 status = "Highly packed"
#             elif total_poc_count >= 2 and total_dev_count == 1:
#                 status = "Occupied"
#             elif total_poc_count >= 2 and total_dev_count == 0:
#                 status = "Partially packed"
#             elif total_poc_count == 0 and total_dev_count == 1:
#                 status = "Partially occupied"
#             elif total_poc_count >= 0 and total_dev_count >= 2:
#                 status = "Occupied"
#             elif total_poc_count == 1 and total_dev_count == 0:
#                 status = "Bench"
#             elif total_poc_count == 0 and total_dev_count == 0:
#                 status = "Bench"
#             else:
#                 status = "Uncategorized"

#             resource_status.append({
#                 'name': resource.resource_name,
#                 'poc_count': total_poc_count,
#                 'dev_count': total_dev_count,
#                 'status': status
#             })

#     resource_count = resources.filter(is_active=True).count()
#     project_count = reports.count()  # ProjectReport count for selected year/month

#     return render(request, 'home.html', {
#         'years': years,
#         'months': months,
#         'year': year,
#         'month': month,
#         'projects': reports,  # renamed to reports
#         'resources': resources,
#         'current_year': now.year,
#         'current_month': now.month,
#         'active_tab': tab,
#         'team_productivity_percentage': team_productivity_percentage,
#         'total_working_days': total_working_days,
#         'total_present_days': total_present_days,
#         'total_present_hours': total_present_hours,
#         'presence_percentage': presence_percentage,
#         'total_billable_days': total_billable_days,
#         'total_non_billable_days': total_non_billable_days,
#         'total_billable_hours': total_billable_hours,
#         'total_non_billable_hours': total_non_billable_hours,
#         'resource_status': resource_status,
#         'resource_count': resource_count,
#         'project_count': project_count
#     })


def project_list(request):
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    projects = Project.objects.all()

    if selected_year:
        projects = projects.filter(start_year=selected_year)
    if selected_month:
        projects = projects.filter(start_month=selected_month)

    years = Project.objects.values_list('start_year', flat=True).distinct().order_by('start_year')
    months = Project.objects.values_list('start_month', flat=True).distinct().order_by('start_month')

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

def add_resource_attendance(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    if request.method == "POST":
        form = ResourceMonthlyForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.resource = resource
            attendance.save()
            return redirect("projects:attendance_home")
    else:
        form = ResourceMonthlyForm()
    return render(request, "attendance/add_resource_attendance.html", {"form": form, "resource": resource})


def add_project_attendance(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectReportForm(request.POST)
        form.fields['project'].queryset = Project.objects.filter(pk=project.pk)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.project = project  # force it anyway
            attendance.save()
            form.save_m2m()
            return redirect("projects:attendance_home")
    else:
        form = ProjectReportForm(initial={"project": project})
        form = ProjectReportForm()
        form.fields['project'].queryset = Project.objects.filter(pk=project.pk)
 
    return render(
        request,
        "attendance/add_project_attendance.html",
        {"form": form, "project": project}
    )
 
def edit_project_attendance(request, pk):
    project=get_object_or_404(ProjectReport,pk=pk)
    if request.method=="POST":
        project_form=ProjectReportForm(request.POST,instance=project)
        project_form.fields['project'].queryset = Project.objects.filter(pk=project.pk)
        if project_form.is_valid():
            project_form.save()
            return redirect("projects:attendance_home")
    else:
        project_form=ProjectReportForm(instance=project)
        project_form.fields['project'].queryset = Project.objects.filter(pk=project.project.pk)
    
    return render(request, 'attendance/edit_project_attendance.html', {
        'form': project_form,
        'title': 'Edit Project Attendance',
        'attendance': project
    })

def edit_resource_attendance(request,pk):
    resources=get_object_or_404(ResourceMonthlyData,pk=pk)
    if request.method=="POST":
        form=ResourceMonthlyForm(request.POST,instance=resources)
        # form.fields['monthly_data'].queryset = Resource.objects.filter(pk=resources.pk)
        if form.is_valid():
            form.save()
            return redirect("projects:attendance_home")
    else:
        form=ResourceMonthlyForm(instance=resources)
        # form.fields['monthly_data'].queryset = Resource.objects.filter(pk=resources.monthly_data.pk)
    
    return render(request, 'attendance/edit_resource_attendance.html', {
        'form': form,
        'title': 'Edit Resource Attendance',
        'attendance': resources
    })

def attendance_home(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))
    resources = Resource.objects.all()
    projects = Project.objects.all()
    resourceAttendance = ResourceMonthlyData.objects.filter(
     year=selected_year, month=selected_month
    )
    projectAttendance = ProjectReport.objects.filter(
     year=selected_year, month=selected_month
    )
    
    resources_with_attendance = []
    for resource in resources:
        current_attendance = resource.monthly_data.filter(
            year=selected_year,
            month=selected_month
        ).first()

        resources_with_attendance.append({
            "resource": resource,
            "attendance": current_attendance
        })

    projects_with_attendance = []
    for project in projects:
        current_proj_attendance = project.reports.filter(
            year = selected_year,
            month = selected_month
        ).first()

        projects_with_attendance.append({
            "project": project,
            "attendance": current_proj_attendance
        })

    # Totals (resource attendance)
    total_working_days = sum(r.working_days  for r in resourceAttendance)
    total_present_days_resources = sum(r.present_day  for r in resourceAttendance)
    total_present_hours = sum(r.present_hours  for r in resourceAttendance)
    presence_percentage = (100 * total_present_days_resources) / total_working_days if total_working_days else 0

    # Totals (project attendance)
    total_present_days_projects = sum(p.present_day  for p in projectAttendance)
    total_billable_days = sum(p.billable_days  for p in projectAttendance)
    total_non_billable_days = sum(p.non_billable_days for p in projectAttendance)
    total_billable_hours = sum(p.billable_hours for p in projectAttendance)
    total_non_billable_hours = sum(p.non_billable_hours for p in projectAttendance)

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    context = {
        "resources_with_attendance": resources_with_attendance,
        "projects_with_attendance": projects_with_attendance,
        "projects": projects,
        "projectAttendance": projectAttendance,
        "total_working_days": total_working_days,
        "total_present_days_resources": total_present_days_resources,
        "total_present_hours": total_present_hours,
        "total_present_days_projects":total_present_days_projects,
        "total_billable_days": total_billable_days,
        "total_non_billable_days": total_non_billable_days,
        "total_billable_hours": total_billable_hours,
        "total_non_billable_hours": total_non_billable_hours,
        "presence_percentage": presence_percentage,
        "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
    }

    return render(request, 'attendance/attendance_home.html', context)

def tree_structure_view(request):
    projects = Project.objects.filter(is_active=True).prefetch_related(
        'reports__project_profile',  
        'reports__resources',        
        'reports__poc'               
    )

    # Fetch all active resources and annotate latest year/month from reports
    resources = Resource.objects.filter(is_active=True).annotate(
        latest_year=Max('monthly_data__year'),
        latest_month=Max('monthly_data__month')
    ).order_by('-latest_year', '-latest_month', 'resource_name')

    # Handle selected project 
    selected_project_id = request.GET.get('project')
    selected_project = None
    if selected_project_id:
        try:
            selected_project = projects.get(id=selected_project_id)
        except Project.DoesNotExist:
            selected_project = None
    if not selected_project and projects.exists():
        selected_project = projects.first()

    # Group projects by year-month using reports 
    projects_by_period = {}
    for project in projects:
        for report in project.reports.all():
            period_key = f"{report.year}-{report.month:02d}"
            projects_by_period.setdefault(period_key, {
                'year': report.year,
                'month': report.month,
                'month_name': calendar.month_name[report.month],
                'projects': []
            })['projects'].append(report)
    
    sorted_periods = sorted(projects_by_period.keys(), reverse=True)

    # Handle selected resource 
    selected_resource_id = request.GET.get('resource')
    selected_resource = None
    assigned_projects = []

    if selected_resource_id:
        try:
            selected_resource = resources.get(id=selected_resource_id)
            # Fetch assigned projects for a selected resource
            assigned_projects_qs = ProjectReport.objects.filter(
                Q(resources=selected_resource) | Q(poc=selected_resource)
            ).select_related('project', 'project_profile').prefetch_related('resources', 'poc').distinct()
            assigned_projects = list(assigned_projects_qs)
        except Resource.DoesNotExist:
            selected_resource = None
    if not selected_resource and resources.exists():
        selected_resource = resources.first()

    # Group resources by latest year-month 
    resources_by_period = {}
    for resource in resources:
        year = resource.latest_year or 0
        month = resource.latest_month or 0
        period_key = f"{year}-{month:02d}"
        resources_by_period.setdefault(period_key, {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month] if month else 'N/A',
            'resources': []
        })['resources'].append(resource)

    sorted_resource_periods = sorted(resources_by_period.keys(), reverse=True)

    # Summary statistics over reports 
    all_reports = ProjectReport.objects.filter(project__in=projects)
    total_projects = projects.count()
    total_resources = resources.count()
    total_billable_hours = sum(r.billable_hours for r in all_reports)
    total_non_billable_hours = sum(r.non_billable_hours for r in all_reports)
    total_hours = total_billable_hours + total_non_billable_hours

    context = {
        'projects_by_period': projects_by_period,
        'sorted_periods': sorted_periods,
        'selected_project': selected_project,
        'resources_by_period': resources_by_period,
        'sorted_resource_periods': sorted_resource_periods,
        'selected_resource': selected_resource,
        'assigned_projects': assigned_projects,
        'total_projects': total_projects,
        'total_resources': total_resources,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
        'total_hours': total_hours,
    }

    return render(request, 'projects/tree_structure.html', context)

