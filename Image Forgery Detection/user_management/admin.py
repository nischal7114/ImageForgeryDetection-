from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Extend UserAdmin to include Groups in User model
class UserAdmin(BaseUserAdmin):
    fieldsets = [
        (None, {'fields': ['username', 'password']}),
        ('Personal Info', {'fields': ['first_name', 'last_name', 'email']}),
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}),
        ('Important Dates', {'fields': ['last_login', 'date_joined']}),
    ]

# Unregister User (to modify it)
if admin.site.is_registered(User):
    admin.site.unregister(User)

# Register User with extended admin
admin.site.register(User, UserAdmin)

# FIX: Avoid registering Group if already registered
try:
    admin.site.register(Group)
except admin.sites.AlreadyRegistered:
    pass  # Avoids the error if Group is already registered
