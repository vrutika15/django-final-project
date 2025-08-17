from django.contrib import admin
from .models import Resource, ResourceMonthlyData

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'resource_name',
        'join_date',
        'leave_date',
        'is_active',
    )
    search_fields = ('resource_name',)
    list_filter = ('is_active',)
    ordering = ['resource_name']

@admin.register(ResourceMonthlyData)
class ResourceMonthlyDataAdmin(admin.ModelAdmin):
    list_display = (
        'resource',
        'year',
        'month',
        'working_days',
        'present_day',
        'present_hours',
        'created_at',
    )
    search_fields = ('resource__resource_name',)
    list_filter = ('year', 'month')
    ordering = ['-year', '-month', 'resource']
