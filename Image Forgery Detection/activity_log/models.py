from django.db import models
from django.contrib.auth.models import User
from case_management.models import Case
from image_verification.models import CaseImage

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    case = models.ForeignKey('case_management.Case', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ForeignKey('image_verification.CaseImage', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)

def log_activity(user, action, case, image=None, details=None):
    ActivityLog.objects.create(
        user=user,
        action=action,
        case=case,
        image=image,
        details=details
    )