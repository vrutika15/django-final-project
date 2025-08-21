from django.contrib import admin
from .models import Project, ProjectReport

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_name',
        'project_type',
        'start_year',
        'start_month',
        'end_year',
        'end_month',
        'is_active',
        'created_at',
        'updated_at',
    )
    search_fields = ('project_name',)
    list_filter = ('project_type','is_active', 'start_year', 'start_month', 'end_year', 'end_month')
    ordering = ['project_name']

@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        
        'year',
        'month',
        'project_profile',
        'present_day',
        'billable_days',
        'non_billable_days',
        'billable_hours',
        'non_billable_hours',
        'extra_hours',
        'counting',
        'resource_count',
        'utilization_percentage',
        'created_at',
        'updated_at',
    )
    list_filter = ( 'year', 'month')
    search_fields = ('project__project_name', 'project_profile__resource_name')
    filter_horizontal = ('resources', 'poc')
    readonly_fields = ('billable_hours', 'non_billable_hours', 'created_at', 'updated_at')
    ordering = ['-year', '-month', 'project__project_name']
