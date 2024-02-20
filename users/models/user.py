import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from users.validators.auth import validate_name
from phonenumber_field import modelfields
from django.core.mail import send_mail
from ..utils.sms import SMS


class User(AbstractUser):
    class Themes(models.TextChoices):
        DARK = "dark", _("Dark")
        LIGHT = "light", _("Light")

    class Genders(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NONE = "N", _("Not specified")

    class Languages(models.TextChoices):
        ENGLISH = "en", _("English")
        RUSSIAN = "ru", _("Russian")
        TURKMEN = "tk", _("Turkmen")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone_number = modelfields.PhoneNumberField(null=True, blank=True, unique=True)

    # SECURITY
    two_factor_auth = models.BooleanField(default=False)
    recovery_email = models.EmailField()

    # PROFILE INFO
    first_name = models.CharField(max_length=100, validators=[validate_name])
    last_name = models.CharField(max_length=100, validators=[validate_name], null=True, blank=True)
    avatar = models.FileField(upload_to='avatars/')
    birthday = models.DateField()
    gender = models.CharField(max_length=20, choices=Genders, default=Genders.NONE)

    # USER SETTINGS
    theme = models.CharField(max_length=10, choices=Themes, default=Themes.LIGHT)
    language = models.CharField(max_length=10, choices=Languages, default=Languages.TURKMEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def send_email(self, subject, message):
        try:
            send_mail(
                subject,
                message,
                settings.NOTIFIER_EMAIL,
                [self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            return False

    def send_message(self, message):
        sms_api = SMS(message, self.phone_number)
        try:
            sms_api.send()
            return True
        except Exception as e:
            return False
