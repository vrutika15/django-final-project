from django.db import models
from resources.models import Resource
from django.core.validators import MinValueValidator
from django.urls import reverse
import calendar

# Create your models here.

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

    year = models.PositiveIntegerField(
        help_text="Enter the year for this project report (e.g., 2025)"
    )

    month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        help_text="Enter the month for this project report (1–12)"
    )

    #project profile which can be selected multiple
    project_profile = models.ForeignKey(
        Resource,
        on_delete=models.PROTECT,
        related_name='profiled_projects',
        help_text="Main profile/resource for this project"
    )

    resources = models.ManyToManyField(
        Resource,
        related_name='assigned_projects',
        help_text="Multiple resources can be assigned to this project"
    )

    # POC (Point of Contact) field - multiple selection
    poc = models.ManyToManyField(
        Resource,
        related_name='poc_projects',
        blank=True,
        help_text="Multiple POCs can be assigned to this project"
    )

    present_day = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of days the project was active"
    )

    billable_days = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of billable days"
    )

    non_billable_days = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of non-billable days"
    )

    billable_hours = models.FloatField(
        default=0,
        editable=False,
        help_text="Auto-calculated from billable_days × 8"
    )

    non_billable_hours = models.FloatField(
        default=0,
        editable=False,
        help_text="Auto-calculated from non_billable_days × 8"
    )   

    extra_hours = models.FloatField(
        null=True,
        blank=True,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Any additional hours (optional)"
    )

    is_active = models.BooleanField(default=True, help_text="For soft deletion")
    created_at = models.DateTimeField(auto_now_add=True)
    counting = models.FloatField(default=0, help_text="Counting value")
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
        standard_hours = 8 * 22  # Assuming 22 working days/month
        if standard_hours == 0:
            return 0
        utilization = (self.total_hours / standard_hours) * 100
        return min(utilization, 100)

    @property
    def resource_count(self):
        return self.resources.count()

    def __str__(self):
        resource_names = ", ".join([resource.resource_name for resource in self.resources.all()[:3]])
        if self.resource_count > 3:
            resource_names += f" (+{self.resource_count - 3} more)"
        return f"{self.project_name} ({calendar.month_name[self.month]} {self.year}) → {resource_names}"

    def get_absolute_url(self):
        return reverse('projects:project_detail', args=[str(self.id)])

    class Meta:
        db_table = 'projects'
        ordering = ['-year', '-month', 'project_name']
        # unique_together = ('project_name', 'year', 'month')
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'