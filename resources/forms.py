# forms.py

from django import forms
from .models import Resource, ResourceMonthlyData

class ResourceGlobalForm(forms.ModelForm):
    # Only for global details
    class Meta:
        model = Resource
        fields = ['resource_name', 'join_date', 'leave_date', 'is_active']
        widgets = {
            'resource_name': forms.TextInput(attrs={'class': 'form-control'}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'leave_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ResourceMonthlyForm(forms.ModelForm):
    # For month-specific details
    class Meta:
        model = ResourceMonthlyData
        fields = ['year', 'month', 'working_days', 'present_day', 'present_hours', 'counting']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control'}),
            'working_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Leave blank for auto-calculation'
            }),
            'present_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'present_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'counting': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'present_day': 'Days Present',
            'present_hours': 'Hours Present',
            'counting': 'Include in Calculation'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['working_days'].required = False
        if self.instance and self.instance.pk:
            self.fields['working_days'].help_text = f"Auto-calculated value: {getattr(self.instance, 'get_working_days_for_display', lambda: '')()}"
        else:
            self.fields['working_days'].help_text = "Auto-calculated if left blank."

    def clean(self):
        cleaned_data = super().clean()
        resource_name = getattr(self.instance, 'resource_name', None)
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')
        # if resource_name and year and month:
        #     qs = ResourceModel.objects.filter(resource_name=resource_name, year=year, month=month)
        #     if self.instance.pk:
        #         qs = qs.exclude(pk=self.instance.pk)
        #     if qs.exists():
        #         from django.core.exceptions import ValidationError
        #         raise ValidationError("A record for this resource already exists for this month and year.")
        return cleaned_data
