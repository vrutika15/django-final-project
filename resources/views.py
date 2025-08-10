from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource
from .forms import ResourceForm
from django.contrib import messages
from calendar import month_name
 
 
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

 