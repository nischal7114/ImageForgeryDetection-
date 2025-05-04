from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class ActiveUserBackend(ModelBackend):
    """ Custom authentication backend that restricts inactive users. """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
        return None
