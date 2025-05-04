from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class UserManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_management"

    def ready(self):
        """Ensure roles and permissions are created on startup."""
        try:
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.auth.models import User

            def create_roles():
                """Create default user roles and assign permissions."""
                admin_group, _ = Group.objects.get_or_create(name="Admin")
                investigator_group, _ = Group.objects.get_or_create(name="Investigator")
                viewer_group, _ = Group.objects.get_or_create(name="Viewer")

                content_type = ContentType.objects.get_for_model(User)

                # Admin - Full Permissions
                permissions = Permission.objects.filter(content_type=content_type)
                admin_group.permissions.set(permissions)

                # Investigator - Limited Permissions
                investigator_permissions = Permission.objects.filter(
                    content_type=content_type,
                    codename__in=["add_caseimage", "change_caseimage", "view_caseimage"]
                )
                investigator_group.permissions.set(investigator_permissions)

                # Viewer - Read-Only Permissions
                viewer_permissions = Permission.objects.filter(
                    content_type=content_type, codename__in=["view_caseimage"]
                )
                viewer_group.permissions.set(viewer_permissions)

            create_roles()

        except (OperationalError, ProgrammingError):
            print("Skipping role creation - Database not ready yet.")
