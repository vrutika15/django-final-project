import calendar
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Technology, Intern
from .forms import TechnologyForm, InternForm
from resources.models import Resource,ResourceMonthlyData
from projects.models import Project,ProjectReport
from django.http import HttpResponseForbidden

#list all tech
def technology_list(request):
    role = request.session.get('role')
    if role not in ['admin', 'superadmin']:
        return HttpResponseForbidden("Not allowed")
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
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
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
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
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
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
    tech = get_object_or_404(Technology, pk=pk)
    if request.method == 'POST':
        tech.delete()
        return redirect('interns:technology_list')
    return render(request, 'technologies/technology_confirm_delete.html', {'technology': tech})

#interns

#list intern
def intern_list(request):
    role = request.session.get('role')
    if role not in ['admin', 'superadmin']:
        return HttpResponseForbidden("Not allowed")
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    interns = Intern.objects.filter(year=selected_year, month=selected_month)

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    return render(request, 'interns/intern_list.html', {'interns': interns,"years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,})

#create intern
def intern_create(request):
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
    selected_year = int(request.GET.get("year", timezone.now().year))
    selected_month = int(request.GET.get("month", timezone.now().month))

    if request.method == 'POST':
        form = InternForm(request.POST)
        if form.is_valid():
            intern = form.save(commit=False)
            intern.year = selected_year
            intern.month = selected_month
            intern.save()
            form.save_m2m()
            return redirect(f"{reverse('interns:intern_list')}?year={selected_year}&month={selected_month}")
    else:
        form = InternForm()
    
    return render(request, 'interns/intern_form.html', {
        'form': form,
        'title': 'Add Intern',
        'year': selected_year,
        'month': selected_month,
    })


#edit intern
def intern_edit(request, pk):
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
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
    role = request.session.get('role')
    if role != 'admin':
        return HttpResponseForbidden("Not allowed")
    intern = get_object_or_404(Intern, pk=pk)
    if request.method == 'POST':
        intern.delete()
        return redirect('interns:intern_list')
    return render(request, 'interns/intern_confirm_delete.html', {'intern': intern})


#navigation-card
#resources
def resources(request):
    role = request.session.get('role')
    if role not in ['user', 'admin', 'superadmin']:
        return HttpResponseForbidden("Not allowed")
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    resources = Resource.objects.filter(is_active=True)
    resourceAttendance = ResourceMonthlyData.objects.filter(
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

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    context = {
        "resources": resources,
        "resourceAttendance": resourceAttendance,
        "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
        "resources_with_attendance": resources_with_attendance,
    }

    return render(request,"navigation-cards/resources.html",context)

#projects
def projects(request):
    role = request.session.get('role')
    if role not in ['user', 'admin', 'superadmin']:
        return HttpResponseForbidden("Not allowed")
    current_year = timezone.now().year
    current_month = timezone.now().month
    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    projects = Project.objects.filter(is_active=True)
    projectAttendance = ProjectReport.objects.filter(year=selected_year, month=selected_month)

    projects_with_attendance = []
    for project in projects:
        current_attendance = project.reports.filter(
            year = selected_year,
            month = selected_month
        ).first() 
        projects_with_attendance.append({
            "project": project,
            "attendance": current_attendance
        })

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    context = {
        "projects": projects,
        "projectAttendance": projectAttendance,
        "projects_with_attendance": projects_with_attendance,
       "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
        "projects_with_attendance": projects_with_attendance,
    }

    return render(request,"navigation-cards/projects.html",context)

#manage resources
def determine_resource_status(poc_count, dev_count):
    if poc_count >= 5 and dev_count == 0:
        return "Highly packed"
    elif poc_count >= 2 and dev_count == 1:
        return "Occupied"
    elif poc_count >= 2 and dev_count == 0:
        return "Partially packed"
    elif poc_count == 0 and dev_count == 1:
        return "Partially occupied"
    elif poc_count >= 0 and dev_count >= 2:
        return "Occupied"
    elif poc_count == 1 and dev_count == 0:
        return "Bench"
    elif poc_count == 0 and dev_count == 0:
        return "Bench"
    else:
        return "Uncategorized"


def manage_resources(request):
    role = request.session.get('role')
    if role not in ['user', 'admin', 'superadmin']:
        return HttpResponseForbidden("Not allowed")
    current_year = timezone.now().year
    current_month = timezone.now().month

    selected_year = int(request.GET.get("year", current_year))
    selected_month = int(request.GET.get("month", current_month))

    reports = ProjectReport.objects.filter(year=selected_year, month=selected_month)

    resources = Resource.objects.filter(is_active=True)
    resource_status = []

    for resource in resources:
        poc_count = reports.filter(poc=resource).count()
        dev_count = reports.filter(resources=resource).count()

        status = determine_resource_status(poc_count, dev_count)

        resource_status.append({
            'name': resource.resource_name,
            'poc_count': poc_count,
            'dev_count': dev_count,
            'status': status
        })

    years = range(current_year - 5, current_year + 1)
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    return render(request, "navigation-cards/manage_resources.html", {
        "resource_status": resource_status,
        "years": years,
        "year": selected_year,
        "months": months,
        "month": selected_month,
    })

#convert intern to resource
def intern_edit(request, pk):
    intern = get_object_or_404(Intern, pk=pk)
    if request.method == 'POST':
        form = InternForm(request.POST, instance=intern)
        if form.is_valid():
            intern_instance = form.save()  # Save intern and M2M fields first
            # Handle conversion to resource
            if form.cleaned_data.get('convert_to_resource'):
                Resource.objects.create(
                    resource_name=intern_instance.name,
                    join_date=date.today(),
                    is_active=True
                )
                intern_instance.delete()  # now safe to delete the intern
            return redirect('interns:intern_list')
    else:
        form = InternForm(instance=intern)
    return render(request, 'interns/intern_form.html', {'form': form, 'title': 'Edit Intern'})