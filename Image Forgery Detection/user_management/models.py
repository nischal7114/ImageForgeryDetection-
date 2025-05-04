from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class UserStatus(models.TextChoices):
    ACTIVE = "Active", "Active"
    INACTIVE = "Inactive", "Inactive"
    SUSPENDED = "Suspended", "Suspended"

class CustomUser(AbstractUser):
    """Extended User model with role-based access control (RBAC)"""
    role = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=UserStatus.choices, default=UserStatus.ACTIVE
    )
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"
