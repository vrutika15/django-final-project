from django import forms
from .models import Technology, Intern

#technology form
class TechnologyForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

#intern form
class InternForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = [
            'name',
            'tech_stack',
            'communication_rating',
            'attitude_rating',
            'task_provided',
            'task_frequency',
            'task_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tech_stack': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'communication_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 10}),
            'attitude_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 10}),
            'task_provided': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'task_frequency': forms.Select(attrs={'class': 'form-select'}),
            'task_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }