from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from activity_log.views import activity_log_list, download_logs_pdf

def redirect_to_login(request):
    """Redirects root URL to login if user is not authenticated."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")

urlpatterns = [
    path("", redirect_to_login, name="home"),
    path("admin/", admin.site.urls),
    path("", include("user_management.urls")),
    path("cases/", include("case_management.urls")),
    path("images/", include("image_verification.urls")),
    path("activity-log/", activity_log_list, name="activity_log_list"),
    path("activity-log/download/", download_logs_pdf, name="download_logs_pdf"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)