import calendar
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Intern(models.Model):
    TASK_FREQUENCY_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    name = models.CharField(max_length=100)

    tech_stack = models.ManyToManyField(
        Technology,
        help_text="Select multiple technologies the intern is working on."
    )

    communication_rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rating out of 10"
    )
    attitude_rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rating out of 10"
    )
    overall_rating = models.FloatField(
        editable=False,
        default=0,
        help_text="Auto-calculated average rating"
    )

    task_provided = models.BooleanField(default=False)
    task_frequency = models.CharField(
        max_length=10,
        choices=TASK_FREQUENCY_CHOICES,
        blank=True,
        null=True
    )

    task_description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the task assigned to the intern"
    )

    convert_to_resource = models.BooleanField(default=False)
    
    year = models.IntegerField(null=True, blank=True)

    month = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.overall_rating = round(
            (self.communication_rating + self.attitude_rating) / 2, 2
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
