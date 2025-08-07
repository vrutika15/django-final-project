from django import forms
from .models import Project
from resources.models import Resource
from datetime import date

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # Exclude auto-calculated and system fields
        fields = [
            'project_name', 'project_type', 'year', 'month', 'project_profile', 'resources', 'poc',
            'present_day', 'billable_days', 'non_billable_days', 'extra_hours', 'is_active'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 2000, 'max': 2100, 'placeholder': 'Year (e.g. 2025)'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'project_profile': forms.Select(attrs={'class': 'form-select'}),
            'resources': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'poc': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'present_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'billable_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'non_billable_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'extra_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'project_name': 'Project Name',
            'project_type': 'Type',
            'present_day': 'Days Present',
            'billable_days': 'Billable Days',
            'non_billable_days': 'Non-Billable Days',
            'extra_hours': 'Extra Hours',
            'project_profile': 'Project Profile',
            'resources': 'Assigned Resources',
            'poc': 'Point of Contact (POC)',
            'is_active': 'Active?',
        }
        help_texts = {
            'project_profile': 'Select the main project profile resource.',
            'resources': 'Hold Ctrl (Windows) or Command (Mac) to select multiple resources.',
            'poc': 'Hold Ctrl (Windows) or Command (Mac) to select multiple POCs.',
            'month': 'Month for this project report',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #optional fields
        self.fields['resources'].required=False
        self.fields['poc'].required=False
        
        # Set initial year/month to current if not provided
        if not self.initial.get('year'):
            self.initial['year'] = date.today().year
        if not self.initial.get('month'):
            self.initial['month'] = date.today().month
        #order resources by name
        self.fields['resources'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')
        self.fields['project_profile'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')
        self.fields['poc'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')

    def clean(self):
        cleaned_data = super().clean()
        billable = cleaned_data.get('billable_days') or 0
        non_billable = cleaned_data.get('non_billable_days') or 0
        present = cleaned_data.get('present_day') or 0

        #ensure no negative values for days
        if billable < 0 or non_billable < 0 or present < 0:
            raise forms.ValidationError("Days cannot be negative.")

        #sum of billable + non-billable days does not exceed present days
        if billable > present:
            raise forms.ValidationError("Billable days cannot be more than present days.")

        return cleaned_data

    #func if the inactive project profile is selected
    def clean_project_profile(self):
        project_profile = self.cleaned_data.get('project_profile')
        if project_profile and not project_profile.is_active:
            raise forms.ValidationError("Selected project profile resource is inactive.")
        return project_profile
    
    #func if inactive resources are selected
    def clean_resources(self):
        resources = self.cleaned_data.get('resources')
        if resources:
            inactive = resources.filter(is_active=False)
            if inactive.exists():
                raise forms.ValidationError("One or more selected resources are inactive.")
        return resources
    
    #func if inactive POCs are selected
    def clean_poc(self):
        pocs = self.cleaned_data.get('poc')
        if pocs:
            inactive = pocs.filter(is_active=False)
            if inactive.exists():
                raise forms.ValidationError("One or more selected POCs are inactive.")
        return pocs