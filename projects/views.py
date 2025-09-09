from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Project, ProjectReport
from .forms import ProjectForm
from resources.models import Resource, ResourceMonthlyData
from django.db.models import  Q
from django.contrib import messages
from django.utils import timezone
import calendar
from resources.forms import ResourceMonthlyForm
from django.http import HttpResponseForbidden
from projects.forms import ProjectReportForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import openpyxl


def project_list(request):
    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")

    projects = Project.objects.all()

    if selected_year:
        projects = projects.filter(start_year=selected_year)
    if selected_month:
        projects = projects.filter(start_month=selected_month)

    years = (
        Project.objects.values_list("start_year", flat=True)
        .distinct()
        .order_by("start_year")
    )
    months = (
        Project.objects.values_list("start_month", flat=True)
        .distinct()
        .order_by("start_month")
    )

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "years": years,
            "months": months,
            "selected_year": selected_year,
            "selected_month": selected_month,
            "role": request.session.get("role"),
        },
    )


def project_create(request):
    role = request.session.get("role")
    if role not in ["user", "admin"]:
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project_form.save()
            return redirect("projects:project_list")
    else:
        year = request.session.get("selected_year")
        month = request.session.get("selected_month")
        project_form = ProjectForm(initial={"year": year, "month": month})

    return render(
        request,
        "projects/project_form.html",
        {"form": project_form, "title": "Create Project"},
    )


def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    role = request.session.get("role")
    if role not in ["user", "admin"]:
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        project_form = ProjectForm(request.POST, instance=project)
        if project_form.is_valid():
            project_form.save()
            return redirect("projects:project_list")
    else:
        project_form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {"form": project_form, "title": "Edit Project"},
    )


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    role = request.session.get("role")
    if role != "admin":
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        project.is_active = False
        project.save()
        messages.success(
            request, f"Project '{project.project_name}' was marked as inactive."
        )
        return redirect("projects:project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})


def add_resource_attendance(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    role = request.session.get("role")
    if role not in ["user", "admin"]:
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        form = ResourceMonthlyForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.resource = resource
            attendance.save()
            return redirect("projects:attendance_home")
    else:
        form = ResourceMonthlyForm()
    return render(
        request,
        "attendance/add_resource_attendance.html",
        {"form": form, "resource": resource},
    )


# def add_project_attendance(request, project_id):
#     project = get_object_or_404(Project, pk=project_id)
#     role = request.session.get("role")
#     if role not in ["user", "admin"]:
#         return HttpResponseForbidden("Not allowed")
#     if request.method == "POST":
#         form = ProjectReportForm(request.POST)
#         form.fields["project"].queryset = Project.objects.filter(pk=project.pk)
#         if form.is_valid():
#             attendance = form.save(commit=False)
#             attendance.project = project  # force it anyway
#             attendance.save()
#             form.save_m2m()
#             return redirect("projects:attendance_home")
#     else:
#         form = ProjectReportForm(initial={"project": project})
#         form = ProjectReportForm()
#         form.fields["project"].queryset = Project.objects.filter(pk=project.pk)

#     return render(
#         request,
#         "attendance/add_project_attendance.html",
#         {"form": form, "project": project},
#     )

def add_project_attendance(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    role = request.session.get("role")
    if role not in ["user", "admin"]:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = ProjectReportForm(request.POST)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.project = project  # Assign the project explicitly
            new_report.save()
            form.save_m2m()
            return redirect("projects:attendance_home")
    else:
        form = ProjectReportForm()

    return render(
        request,
        "attendance/add_project_attendance.html",
        {
            "form": form,
            "project": project,
            "title": "Add Project Attendance"
        }
    )


# def edit_project_attendance(request, pk):
#     project=get_object_or_404(ProjectReport,pk=pk)
#     role = request.session.get('role')
#     if role not in ['user', 'admin']:
#         return HttpResponseForbidden("Not allowed")
#     if request.method=="POST":
#         project_form=ProjectReportForm(request.POST,instance=project)
#         project_form.fields['project'].queryset = ProjectReport.objects.filter(pk=project.pk)
#         if project_form.is_valid():
#             project_form.save()
#             return redirect("projects:attendance_home")
#     else:
#         project_form=ProjectReportForm(instance=project)
#         project_form.fields['project'].queryset = Project.objects.filter(pk=project.project.pk)
    
#     return render(request, 'attendance/edit_project_attendance.html', {
#         'form': project_form,
#         'title': 'Edit Project Attendance',
#         'attendance': project
#     })

def edit_project_attendance(request, pk):
    project_report = get_object_or_404(ProjectReport, pk=pk)
    role = request.session.get('role')
    if role not in ['user', 'admin']:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = ProjectReportForm(request.POST, instance=project_report)
        if form.is_valid():
            updated_report = form.save(commit=False)
            updated_report.project = project_report.project  # Reassign the project
            updated_report.save()
            form.save_m2m()
            return redirect("projects:attendance_home")
    else:
        form = ProjectReportForm(instance=project_report)

    return render(request, 'attendance/edit_project_attendance.html', {
        'form': form,
        'title': 'Edit Project Attendance',
        'attendance': project_report
    })


def edit_resource_attendance(request, pk):
    resources = get_object_or_404(ResourceMonthlyData, pk=pk)
    role = request.session.get("role")
    if role not in ["user", "admin"]:
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        form = ResourceMonthlyForm(request.POST, instance=resources)
        if form.is_valid():
            form.save()
            return redirect("projects:attendance_home")
    else:
        form = ResourceMonthlyForm(instance=resources)

    return render(
        request,
        "attendance/edit_resource_attendance.html",
        {"form": form, "title": "Edit Resource Attendance", "attendance": resources},
    )


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
            year=selected_year, month=selected_month
        ).first()

        resources_with_attendance.append(
            {"resource": resource, "attendance": current_attendance}
        )

    projects_with_attendance = []
    for project in projects:
        current_proj_attendance = project.reports.filter(
            year=selected_year, month=selected_month
        ).first()

        projects_with_attendance.append(
            {"project": project, "attendance": current_proj_attendance}
        )

    # Totals (resource attendance)
    total_working_days = sum(r.working_days for r in resourceAttendance)
    total_present_days_resources = sum(r.present_day for r in resourceAttendance)
    total_present_hours = sum(r.present_hours for r in resourceAttendance)
    presence_percentage = (
        (100 * total_present_days_resources) / total_working_days
        if total_working_days
        else 0
    )

    # Totals (project attendance)
    total_present_days_projects = sum(p.present_day for p in projectAttendance)
    total_billable_days = sum(p.billable_days for p in projectAttendance)
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
        "total_present_days_projects": total_present_days_projects,
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

    return render(request, "attendance/attendance_home.html", context)


def tree_structure_view(request):
    # Get year and month from request or use current date
    year_param = request.GET.get('year')
    month_param = request.GET.get('month')
    
    now = datetime.now()
    try:
        year = int(year_param) if year_param else now.year
    except ValueError:
        year = now.year
    try:
        month = int(month_param) if month_param else now.month
    except ValueError:
        month = now.month

    # --- Fetch all active projects with their reports ---
    projects = Project.objects.filter(is_active=True).prefetch_related(
        'reports__project_profile',  
        'reports__resources',        
        'reports__poc'               
    )

    # --- Fetch all active resources with their monthly data ---
    resources = Resource.objects.filter(is_active=True).prefetch_related(
        'monthly_data',
        'assigned_projects__project',
        'poc_projects__project'
    )

    # --- Handle selected project ---
    selected_project_id = request.GET.get('project')
    selected_project = None
    if selected_project_id:
        try:
            selected_project = projects.get(id=selected_project_id)
        except Project.DoesNotExist:
            selected_project = None
    if not selected_project and projects.exists():
        selected_project = projects.first()

    # --- Group projects by year-month using reports ---
    projects_by_period = {}
    for project in projects:
        for report in project.reports.all():
            period_key = f"{report.year}-{report.month:02d}"
            if period_key not in projects_by_period:
                projects_by_period[period_key] = {
                    'year': report.year,
                    'month': report.month,
                    'month_name': calendar.month_name[report.month],
                    'projects': []
                }
            # Only add if project not already in this period
            if not any(p.project.id == project.id for p in projects_by_period[period_key]['projects']):
                projects_by_period[period_key]['projects'].append(report)
    
    sorted_periods = sorted(projects_by_period.keys(), reverse=True)

    # --- Handle selected resource ---
    selected_resource_id = request.GET.get('resource')
    selected_resource = None
    resource_projects = []  # structured projects for the selected resource

    if selected_resource_id:
        try:
            selected_resource = resources.get(id=selected_resource_id)
            # Fetch assigned projects for the selected resource
            assigned_reports = ProjectReport.objects.filter(
                Q(resources=selected_resource) | Q(poc=selected_resource)
            ).select_related('project', 'project_profile').prefetch_related('resources', 'poc').distinct()
            
            # Build unique project entries with aggregated POCs and Resources
            project_dict = {}
            for report in assigned_reports:
                project_key = report.project.id
                if project_key not in project_dict:
                    project_dict[project_key] = {
                        'project': report.project,
                        'pocs': set(),
                        'resources': set()
                    }
                # Add POCs and Resources to sets to avoid duplicates
                project_dict[project_key]['pocs'].update(report.poc.all())
                project_dict[project_key]['resources'].update(report.resources.all())

            # Convert to list format
            resource_projects = [
                {
                    'project': entry['project'],
                    'pocs': list(entry['pocs']),
                    'resources': list(entry['resources']),
                }
                for entry in project_dict.values()
            ]
        except Resource.DoesNotExist:
            selected_resource = None
    if not selected_resource and resources.exists():
        selected_resource = resources.first()

    # --- Group resources by year-month from their monthly data ---
    resources_by_period = {}
    for resource in resources:
        # Get all monthly data for this resource
        monthly_data_list = resource.monthly_data.all()
        if monthly_data_list.exists():
            for monthly_data in monthly_data_list:
                period_key = f"{monthly_data.year}-{monthly_data.month:02d}"
                if period_key not in resources_by_period:
                    resources_by_period[period_key] = {
                        'year': monthly_data.year,
                        'month': monthly_data.month,
                        'month_name': calendar.month_name[monthly_data.month],
                        'resources': []
                    }
                # Only add if resource not already in this period
                if not any(r.id == resource.id for r in resources_by_period[period_key]['resources']):
                    resources_by_period[period_key]['resources'].append(resource)
        else:
            # If no monthly data, put in a default period
            period_key = f"{year}-{month:02d}"
            if period_key not in resources_by_period:
                resources_by_period[period_key] = {
                    'year': year,
                    'month': month,
                    'month_name': calendar.month_name[month],
                    'resources': []
                }
            if not any(r.id == resource.id for r in resources_by_period[period_key]['resources']):
                resources_by_period[period_key]['resources'].append(resource)

    sorted_resource_periods = sorted(resources_by_period.keys(), reverse=True)

    # --- Prepare project tree data for selected project ---
    project_tree_data = None
    if selected_project:
        # Get all reports for the selected project
        project_reports = selected_project.reports.all().prefetch_related('poc', 'resources')
        
        # Aggregate all POCs and Resources from all reports using sets to avoid duplicates
        all_pocs = set()
        all_resources = set()
        
        for report in project_reports:
            all_pocs.update(report.poc.all())
            all_resources.update(report.resources.all())
        
        project_tree_data = {
            'project': selected_project,
            'pocs': list(all_pocs),
            'resources': list(all_resources),
        }

    # --- Summary statistics ---
    all_reports = ProjectReport.objects.filter(project__in=projects)
    total_projects = projects.count()
    total_resources = resources.count()
    total_billable_hours = sum(r.billable_hours for r in all_reports)
    total_non_billable_hours = sum(r.non_billable_hours for r in all_reports)
    total_hours = total_billable_hours + total_non_billable_hours

    # --- Render template ---
    context = {
        'projects_by_period': projects_by_period,
        'sorted_periods': sorted_periods,
        'selected_project': selected_project,
        'project_tree_data': project_tree_data,
        'resources_by_period': resources_by_period,
        'sorted_resource_periods': sorted_resource_periods,
        'selected_resource': selected_resource,
        'resource_projects': resource_projects,
        'total_projects': total_projects,
        'total_resources': total_resources,
        'total_billable_hours': total_billable_hours,
        'total_non_billable_hours': total_non_billable_hours,
        'total_hours': total_hours,
        'current_year': year,
        'current_month': month,
    }

    return render(request, 'projects/tree_structure.html', context)

def export_attendance_pdf(request):
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
            year=selected_year, month=selected_month
        ).first()
        resources_with_attendance.append({
            "resource": resource,
            "attendance": current_attendance
        })

    projects_with_attendance = []
    for project in projects:
        current_proj_attendance = project.reports.filter(
            year=selected_year, month=selected_month
        ).first()
        projects_with_attendance.append({
            "project": project,
            "attendance": current_proj_attendance
        })

    # Totals (resource attendance)
    total_working_days = sum(r.working_days for r in resourceAttendance)
    total_present_days_resources = sum(r.present_day for r in resourceAttendance)
    total_present_hours = sum(r.present_hours for r in resourceAttendance)
    presence_percentage = (
        (100 * total_present_days_resources) / total_working_days
        if total_working_days else 0
    )

    # Totals (project attendance)
    total_present_days_projects = sum(p.present_day for p in projectAttendance)
    total_billable_days = sum(p.billable_days for p in projectAttendance)
    total_non_billable_days = sum(p.non_billable_days for p in projectAttendance)
    total_billable_hours = sum(p.billable_hours for p in projectAttendance)
    total_non_billable_hours = sum(p.non_billable_hours for p in projectAttendance)

    context = {
        "resources_with_attendance": resources_with_attendance,
        "projects_with_attendance": projects_with_attendance,
        "total_working_days": total_working_days,
        "total_present_days_resources": total_present_days_resources,
        "total_present_hours": total_present_hours,
        "total_present_days_projects": total_present_days_projects,
        "total_billable_days": total_billable_days,
        "total_non_billable_days": total_non_billable_days,
        "total_billable_hours": total_billable_hours,
        "total_non_billable_hours": total_non_billable_hours,
        "presence_percentage": presence_percentage,
        "year": selected_year,
        "month": selected_month,
        "month_name": calendar.month_name[selected_month]
    }

    # Render PDF
    html_string = render_to_string("projects/attendance_pdf.html", context)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Attendance_{selected_month}_{selected_year}.pdf"'
    return response

def export_attendance_excel(request):
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
            year=selected_year, month=selected_month
        ).first()
        resources_with_attendance.append({
            "resource": resource,
            "attendance": current_attendance
        })

    projects_with_attendance = []
    for project in projects:
        current_proj_attendance = project.reports.filter(
            year=selected_year, month=selected_month
        ).first()
        projects_with_attendance.append({
            "project": project,
            "attendance": current_proj_attendance
        })

    # Totals 
    total_working_days = sum(r.working_days for r in resourceAttendance)
    total_present_days_resources = sum(r.present_day for r in resourceAttendance)
    total_present_hours = sum(r.present_hours for r in resourceAttendance)
    presence_percentage = (
        (100 * total_present_days_resources) / total_working_days
        if total_working_days else 0
    )

    total_present_days_projects = sum(p.present_day for p in projectAttendance)
    total_billable_days = sum(p.billable_days for p in projectAttendance)
    total_non_billable_days = sum(p.non_billable_days for p in projectAttendance)
    total_billable_hours = sum(p.billable_hours for p in projectAttendance)
    total_non_billable_hours = sum(p.non_billable_hours for p in projectAttendance)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"Attendance {calendar.month_name[selected_month]} {selected_year}"

    # Project 
    sheet.append([f"Projects - {calendar.month_name[selected_month]} {selected_year}"])
    sheet.append([
        "Project Name", "Project Type", "Project Profile", "POC",
        "Extra Hours", "Present Days", "Billable Days",
        "Non-Billable Days", "Billable Hours", "Non-Billable Hours"
    ])

    for item in projects_with_attendance:
        project = item["project"]
        att = item["attendance"]
        sheet.append([
            project.project_name,
            # project.project_type,
            # att.project_profile,
            # att.poc,
            # getattr(project, "project_type", ""),
            # getattr(att, "project_profile", ""),
            # getattr(att, "poc", ""),
            str(getattr(project, "project_type", "") or ""),
            str(getattr(att, "project_profile", "") or ""),
            str(getattr(att, "poc", "no poc") or "no poc"),
            att.extra_hours if att else 0,
            att.present_day if att else 0,
            att.billable_days if att else 0,
            att.non_billable_days if att else 0,
            att.billable_hours if att else 0,
            att.non_billable_hours if att else 0,
        ])

    # Totals row (Projects)
    sheet.append([
        "TOTALS", "", "", "",
        "",  
        total_present_days_projects,
        total_billable_days,
        total_non_billable_days,
        total_billable_hours,
        total_non_billable_hours,
    ])

    sheet.append([])
    sheet.append([])

    # Resource 
    sheet.append([f"Resources - {calendar.month_name[selected_month]} {selected_year}"])
    sheet.append([
        "Resource Name", "Working Days", "Days Present", "Hours Present", "Presence %"
    ])

    for item in resources_with_attendance:
        res = item["resource"]
        att = item["attendance"]
        sheet.append([
            res.resource_name,
            att.working_days if att else 0,
            att.present_day if att else 0,
            att.present_hours if att else 0,
            round(((att.present_day / att.working_days) * 100), 2) if att and att.working_days else 0,
        ])

    # Totals row (Resources)
    sheet.append([
        "TOTALS",
        total_working_days,
        total_present_days_resources,
        total_present_hours,
        round(presence_percentage, 2),
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="attendance_{selected_month}_{selected_year}.xlsx"'
    )

    workbook.save(response)
    return response