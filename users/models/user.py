import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from users.utils.functions import get_valid_phone_number
from phonenumber_field import modelfields
from django.core.mail import send_mail
from ..utils.sms import SMS


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    profile = models.OneToOneField('Profile', on_delete=models.SET_NULL, related_name='user',
                                   null=True, blank=True)

    email_address = models.OneToOneField('Email', on_delete=models.SET_NULL, related_name='user',
                                         null=True, blank=True)
    phone_number = modelfields.PhoneNumberField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        if self.phone_number:
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
