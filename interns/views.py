from django.shortcuts import render, redirect, get_object_or_404
from .models import Technology, Intern
from .forms import TechnologyForm, InternForm

#list all tech
def technology_list(request):
    technologies = Technology.objects.all()
    return render(request, 'technologies/technology_list.html', {'technologies': technologies})

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

#dlete tech
def technology_delete(request, pk):
    tech = get_object_or_404(Technology, pk=pk)
    if request.method == 'POST':
        tech.delete()
        return redirect('interns:technology_list')
    return render(request, 'technologies/technology_confirm_delete.html', {'technology': tech})


#interns


#list intern
def intern_list(request):
    interns = Intern.objects.all()
    return render(request, 'interns/intern_list.html', {'interns': interns})

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
