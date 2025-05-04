from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from case_management.models import Case
from image_verification.models import CaseImage
from .models import ActivityLog

@receiver(post_save, sender=Case)
def log_case_activity(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    ActivityLog.objects.create(
        user=instance.created_by,
        action=f"{action} case '{instance.case_name}'",
        case=instance,
        details=f"Case ID: {instance.id}"
    )

@receiver(post_delete, sender=Case)
def log_case_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.created_by,
        action=f"Deleted case '{instance.case_name}'",
        case=instance,
        details=f"Case ID: {instance.id}"
    )

@receiver(post_save, sender=CaseImage)
def log_case_image_activity(sender, instance, created, **kwargs):
    action = "Uploaded" if created else "Updated"
    ActivityLog.objects.create(
        user=instance.uploaded_by,
        action=f"{action} image for case '{instance.case.case_name}'",
        case=instance.case,
        image=instance,
        details=f"Image ID: {instance.id}"
    )

@receiver(post_delete, sender=CaseImage)
def log_case_image_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.uploaded_by,
        action=f"Deleted image for case '{instance.case.case_name}'",
        case=instance.case,
        image=instance,
        details=f"Image ID: {instance.id}"
    )

@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    ActivityLog.objects.create(
        user=instance,
        action=f"{action} user '{instance.username}'",
        details=f"User ID: {instance.id}"
    )

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance,
        action=f"Deleted user '{instance.username}'",
        details=f"User ID: {instance.id}"
    )