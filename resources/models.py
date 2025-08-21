from django.db import models
import calendar
from datetime import date


class Resource(models.Model):
    resource_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full name of the resource"
    )
    join_date = models.DateField(help_text="Date the resource joined")
    leave_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the resource left (optional)"
    )
    is_active = models.BooleanField(default=True, help_text="Mark inactive if resource left")

    class Meta:
        db_table = 'resources'
        ordering = ['resource_name']
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'

    def __str__(self):
        return self.resource_name

    def is_available_in_month(self, year, month):
        """Check if resource is available in a given month/year."""
        first_of_month = date(year, month, 1)
        last_of_month = date(year, month, calendar.monthrange(year, month)[1])
        return (
            self.join_date <= last_of_month and
            (self.leave_date is None or self.leave_date >= first_of_month)
        )


class ResourceMonthlyData(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='monthly_data')
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)]
    )

    working_days = models.FloatField(
        null=True,
        blank=True,
        default=0,
        help_text="Leave blank to auto-calculate (Mon-Fri + 1st Saturday)"
    )
    present_day = models.FloatField(default=0)
    present_hours = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resource_monthly_data'
        ordering = ['-year', '-month', 'resource']
        #unique_together = ('resource', 'year', 'month')

    def __str__(self):
        return f"{self.resource.resource_name} - {calendar.month_name[self.month]} {self.year}"

    def save(self, *args, **kwargs):
        if not self.working_days:
            self.working_days = self.get_working_days(self.year, self.month)
        if self.present_day and not self.present_hours:
            self.present_hours = self.present_day * 8
        super().save(*args, **kwargs)

    @staticmethod
    def get_working_days(year, month):
        """Calculate working days (Mon-Fri + 1st Saturday)."""
        if not year or not month:
            return 0
        _, num_days = calendar.monthrange(year, month)
        first_day = calendar.monthrange(year, month)[0]
        first_saturday = (5 - first_day) % 7 + 1
        if first_saturday > num_days:
            first_saturday = None

        working_days = sum(
            1 for day in range(1, num_days + 1)
            if (first_day + day - 1) % 7 < 5
        )
        if first_saturday:
            working_days += 1
        return working_days
