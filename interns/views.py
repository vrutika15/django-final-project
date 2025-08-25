import calendar
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Technology, Intern
from .forms import TechnologyForm, InternForm
from resources.models import Resource,ResourceMonthlyData
from projects.models import Project,ProjectReport

#list all tech
def technology_list(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))
    
    technologies = Technology.objects.all()

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]
    return render(request, 'technologies/technology_list.html', {'technologies': technologies,"years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month})

#create new tech
def technology_create(request):
    if request.method == 'POST':
        form = TechnologyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interns:technology_list')
    else:
        form = TechnologyForm()
    return render(request, 'technologies/technology_form.html', {'form': form, 'title': 'Add Technology'})

#edit tech
def technology_edit(request, pk):
    tech = get_object_or_404(Technology, pk=pk)
    if request.method == 'POST':
        form = TechnologyForm(request.POST, instance=tech)
        if form.is_valid():
            form.save()
            return redirect('interns:technology_list')
    else:
        form = TechnologyForm(instance=tech)
    return render(request, 'technologies/technology_form.html', {'form': form, 'title': 'Edit Technology'})

#delete tech
def technology_delete(request, pk):
    tech = get_object_or_404(Technology, pk=pk)
    if request.method == 'POST':
        tech.delete()
        return redirect('interns:technology_list')
    return render(request, 'technologies/technology_confirm_delete.html', {'technology': tech})

#interns

#list intern
def intern_list(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    interns = Intern.objects.all()

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    return render(request, 'interns/intern_list.html', {'interns': interns,"years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,})

#create intern
def intern_create(request):
    if request.method == 'POST':
        form = InternForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interns:intern_list')
    else:
        form = InternForm()
    return render(request, 'interns/intern_form.html', {'form': form, 'title': 'Add Intern'})

#edit intern
def intern_edit(request, pk):
    intern = get_object_or_404(Intern, pk=pk)
    if request.method == 'POST':
        form = InternForm(request.POST, instance=intern)
        if form.is_valid():
            form.save()
            return redirect('interns:intern_list')
    else:
        form = InternForm(instance=intern)
    return render(request, 'interns/intern_form.html', {'form': form, 'title': 'Edit Intern'})

#delete intern
def intern_delete(request, pk):
    intern = get_object_or_404(Intern, pk=pk)
    if request.method == 'POST':
        intern.delete()
        return redirect('interns:intern_list')
    return render(request, 'interns/intern_confirm_delete.html', {'intern': intern})


#navigation-card
#resources
def resources(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    resources = Resource.objects.filter(is_active=True)
    resourceAttendance = ResourceMonthlyData.objects.filter(
    year=year,
    month=month
    )

    resources_with_attendance = []
    for resource in resources:
        current_attendance = resource.monthly_data.filter(
            year=year,
            month=month
        ).first()  
        resources_with_attendance.append({
            "resource": resource,
            "attendance": current_attendance
        })

    context = {
        "resources": resources,
        "resourceAttendance": resourceAttendance,
        "year": year,
        "month": month,
        "resources_with_attendance": resources_with_attendance,
    }

    return render(request,"navigation-cards/resources.html",context)

#projects
def projects(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    projects = Project.objects.filter(is_active=True)
    projectAttendance = ProjectReport.objects.filter(year=year,month=month)

    projects_with_attendance = []
    for project in projects:
        current_attendance = project.reports.filter(
            year=year,
            month=month
        ).first() 
        projects_with_attendance.append({
            "project": project,
            "attendance": current_attendance
        })

    context = {
        "projects": projects,
        "projectAttendance": projectAttendance,
        "projects_with_attendance": projects_with_attendance,
        "year": year,
        "month": month,
        "projects_with_attendance": projects_with_attendance,
    }

    return render(request,"navigation-cards/projects.html",context)

#manage resources
def manage_resources(request):
    resource_status = []
    resources = Resource.objects.filter(is_active=True)

    for resource in resources:
            poc_projects = resource.poc_projects.all()
            assigned_projects = resource.assigned_projects.all()
            all_projects = (poc_projects | assigned_projects).distinct()

            total_poc_count = 0
            total_dev_count = 0

            for project in all_projects:
                if resource in project.poc.all():
                    total_poc_count += 1
                if resource in project.resources.all():
                    total_dev_count += 1

            if total_poc_count >= 5 and total_dev_count == 0:
                status = "Highly packed"
            elif total_poc_count >= 2 and total_dev_count == 1:
                status = "Occupied"
            elif total_poc_count >= 2 and total_dev_count == 0:
                status = "Partially packed"
            elif total_poc_count == 0 and total_dev_count == 1:
                status = "Partially occupied"
            elif total_poc_count >= 0 and total_dev_count >= 2:
                status = "Occupied"
            elif total_poc_count == 1 and total_dev_count == 0:
                status = "Bench"
            elif total_poc_count == 0 and total_dev_count == 0:
                status = "Bench"
            else:
                status = "Uncategorized"

            resource_status.append({
                'name': resource.resource_name,
                'poc_count': total_poc_count,
                'dev_count': total_dev_count,
                'status': status
            })

    return render(request,"navigation-cards/manage_resources.html",{"resource_status":resource_status})