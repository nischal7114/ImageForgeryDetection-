from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="user_management/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/edit/<int:user_id>/", views.user_edit, name="user_edit"),
    path("users/deactivate/<int:user_id>/", views.user_deactivate, name="user_deactivate"),
    path("users/activate/<int:user_id>/", views.user_activate, name="user_activate"),
    path("profile/", views.user_profile, name="profile"),
]
