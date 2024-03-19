import uuid

from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field import modelfields

from apps.users.validators.auth import validate_name
from ..utils.sms import SMS


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class AccountTypes(models.TextChoices):
        PERSONAL = 'personal', _('Personal')
        CHILD = 'child', _('Child')

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
    account_type = models.CharField(max_length=20, choices=AccountTypes, default=AccountTypes.PERSONAL)
    email = models.EmailField(unique=True)
    phone_number = modelfields.PhoneNumberField(unique=True)
    parent_email = models.EmailField(blank=True, null=True)

    # SECURITY
    two_factor = models.BooleanField(default=False)
    recovery_email = models.EmailField(null=True, blank=True)

    # PROFILE INFO
    first_name = models.CharField(max_length=100, validators=[validate_name], null=True, blank=True)
    last_name = models.CharField(max_length=100, validators=[validate_name], null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Genders, default=Genders.NONE)

    # USER SETTINGS
    theme = models.CharField(max_length=10, choices=Themes, default=Themes.LIGHT)
    language = models.CharField(max_length=10, choices=Languages, default=Languages.TURKMEN)

    # STATUSES
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

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
