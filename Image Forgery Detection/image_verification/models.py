from django.db import models
from django.contrib.auth.models import User
from case_management.models import Case

class CaseImage(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='case_images/')
    sha256_hash = models.CharField(max_length=64)
    perceptual_hash = models.CharField(max_length=64, blank=True, null=True)
    digital_signature = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Case: {self.case.case_name}"

class Meta:
    permissions = [
        ("download_caseimage", "Can download case images"),
    ]