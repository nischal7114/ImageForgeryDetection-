from django.db import models
from django.contrib.auth.models import User

class Case(models.Model):
    class CaseStatus(models.TextChoices):
        ONGOING = 'Ongoing', 'Ongoing'
        COMPLETED = 'Completed', 'Completed'
        PENDING = 'Pending', 'Pending'

    case_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=CaseStatus.choices,
        default=CaseStatus.PENDING,
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_name