import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from ..utils.sms import SMS
from django.core.mail import send_mail

from ..validators.user import validate_username
from users.utils.functions import get_valid_phone_number


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, related_name='user',
                                   null=True, blank=True)

    username = models.CharField(max_length=30, unique=True, validators=[validate_username])
    phone_number = models.CharField(max_length=30, unique=True)
    balance = models.FloatField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        self.phone_number = get_valid_phone_number(self.phone_number)
        super(User, self).save(*args, **kwargs)

    def send_email(self, message):
        try:
            send_mail(
                "Gozle ID",
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
