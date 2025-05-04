from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    """Decorator to check if the user belongs to a specific group."""
    def in_group(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            return u.groups.filter(name=group_name).exists()
        return False
    return user_passes_test(in_group, login_url='/login/')