from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, phone_number=None, password=None, **kwargs):
        User = get_user_model()

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        elif email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None
        elif phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return None
        else:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
