from django.db import models
from resources.models import Resource
from django.core.validators import MinValueValidator
from django.urls import reverse
import calendar

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('REGULAR', 'Regular Project'),
        ('FIXED_COST', 'Fixed Cost Project'),
    ]
    project_name = models.CharField(max_length=100)
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='REGULAR'
    )

    start_year = models.PositiveIntegerField(
        help_text="Year when the project starts (e.g., 2025)"
    )
    start_month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        help_text="Month when the project starts (1–12)"
    )

    end_year = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Year when the project ends (leave blank if ongoing)"
    )
    end_month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        null=True, blank=True,
        help_text="Month when the project ends (leave blank if ongoing)"
    )

    is_active = models.BooleanField(default=True, help_text="Soft delete toggle")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name

    def is_active_for_date(self, year, month):
        start = (self.start_year, self.start_month)
        end = (self.end_year or 9999, self.end_month or 12)
        current = (year, month)
        return start <= current <= end

    class Meta:
        db_table = 'projects'
        ordering = ['project_name']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class ProjectReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reports")
    year = models.PositiveIntegerField(
        help_text="Year for this report (e.g., 2025)"
    )
    month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        help_text="Month for this report (1–12)"
    )

    project_profile = models.ForeignKey(
        Resource,
        on_delete=models.PROTECT,
        related_name='profiled_projects',
        help_text="Main profile/resource for this project"
    )
    resources = models.ManyToManyField(
        Resource,
        related_name='assigned_projects',
        blank=True
    )
    poc = models.ManyToManyField(
        Resource,
        related_name='poc_projects',
        blank=True
    )

    present_day = models.FloatField(default=0, validators=[MinValueValidator(0)])
    billable_days = models.FloatField(default=0, validators=[MinValueValidator(0)])
    non_billable_days = models.FloatField(default=0, validators=[MinValueValidator(0)])
    billable_hours = models.FloatField(default=0, editable=False)
    non_billable_hours = models.FloatField(default=0, editable=False)
    extra_hours = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0)])
    counting = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.billable_hours = self.billable_days * 8
        self.non_billable_hours = self.non_billable_days * 8
        super().save(*args, **kwargs)

    @property
    def total_hours(self):
        return self.billable_hours + self.non_billable_hours + self.extra_hours

    @property
    def total_days(self):
        return self.billable_days + self.non_billable_days

    @property
    def utilization_percentage(self):
        standard_hours = 8 * 22  # 22 working days/month
        return min((self.total_hours / standard_hours) * 100, 100) if standard_hours else 0

    @property
    def resource_count(self):
        return self.resources.count()

    def __str__(self):
        resource_names = ", ".join([r.resource_name for r in self.resources.all()[:3]])
        if self.resource_count > 3:
            resource_names += f" (+{self.resource_count - 3} more)"
        return f"{self.project.project_name} ({calendar.month_name[self.month]} {self.year}) → {resource_names}"

    def get_absolute_url(self):
        return reverse('projects:project_detail', args=[str(self.id)])

    class Meta:
        db_table = 'project_reports'
        ordering = ['-year', '-month', 'project__project_name']
