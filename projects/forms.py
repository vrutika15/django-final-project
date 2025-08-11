from django import forms
from .models import Project, ProjectReport
from resources.models import Resource
from datetime import date


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name',
            'start_year', 'start_month',
            'end_year', 'end_month',
            'is_active'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'start_month': forms.Select(attrs={'class': 'form-select'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'end_month': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'project_name': 'Project Name',
            'is_active': 'Active?',
        }


class ProjectReportForm(forms.ModelForm):
    class Meta:
        model = ProjectReport
        fields = [
            'project', 'project_type', 'year', 'month', 'project_profile',
            'resources', 'poc',
            'present_day', 'billable_days', 'non_billable_days', 'extra_hours'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
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
        }
        labels = {
            'project': 'Project',
            'project_type': 'Type',
            'present_day': 'Days Present',
            'billable_days': 'Billable Days',
            'non_billable_days': 'Non-Billable Days',
            'extra_hours': 'Extra Hours',
            'project_profile': 'Project Profile',
            'resources': 'Assigned Resources',
            'poc': 'Point of Contact (POC)',
        }
        help_texts = {
            'project_profile': 'Select the main project profile resource.',
            'resources': 'Hold Ctrl (Windows) or Command (Mac) to select multiple resources.',
            'poc': 'Hold Ctrl (Windows) or Command (Mac) to select multiple POCs.',
            'month': 'Month for this project report',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        # Filter active projects that are within date range
        self.fields['project'].queryset = Project.objects.filter(
            is_active=True
        ).filter(
            start_year__lt=today.year,
        ) | Project.objects.filter(
            is_active=True,
            start_year=today.year,
            start_month__lte=today.month
        )
        self.fields['project'].queryset = self.fields['project'].queryset.filter(
            end_year__gt=today.year
        ) | self.fields['project'].queryset.filter(
            end_year=today.year,
            end_month__gte=today.month
        ).order_by('project_name')

        # Optional fields
        self.fields['resources'].required = False
        self.fields['poc'].required = False

        # Default to current year/month if not set
        if not self.initial.get('year'):
            self.initial['year'] = today.year
        if not self.initial.get('month'):
            self.initial['month'] = today.month

        # Active resources only
        self.fields['resources'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')
        self.fields['project_profile'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')
        self.fields['poc'].queryset = Resource.objects.filter(is_active=True).order_by('resource_name')

    def clean(self):
        cleaned_data = super().clean()
        billable = cleaned_data.get('billable_days') or 0
        non_billable = cleaned_data.get('non_billable_days') or 0
        present = cleaned_data.get('present_day') or 0

        if billable < 0 or non_billable < 0 or present < 0:
            raise forms.ValidationError("Days cannot be negative.")

        if billable > present:
            raise forms.ValidationError("Billable days cannot be more than present days.")

        return cleaned_data

    def clean_project_profile(self):
        project_profile = self.cleaned_data.get('project_profile')
        if project_profile and not project_profile.is_active:
            raise forms.ValidationError("Selected project profile resource is inactive.")
        return project_profile

    def clean_resources(self):
        resources = self.cleaned_data.get('resources')
        if resources:
            inactive = resources.filter(is_active=False)
            if inactive.exists():
                raise forms.ValidationError("One or more selected resources are inactive.")
        return resources

    def clean_poc(self):
        pocs = self.cleaned_data.get('poc')
        if pocs:
            inactive = pocs.filter(is_active=False)
            if inactive.exists():
                raise forms.ValidationError("One or more selected POCs are inactive.")
        return pocs
