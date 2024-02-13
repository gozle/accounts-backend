from django.db import models
from django.utils.translation import gettext_lazy as _


class Activity(models.Model):

    class Activities(models.TextChoices):
        LOGIN = 'login', _('Login')
        LOGOUT = 'logout', _('Logout')
        EMAIL_CHANGED = 'email_changed', _('Email changed')
        PHONE_NUMBER_CHANGED = 'phone_number_changed', _('Phone number changed')
        PASSWORD_CHANGED = 'password_changed', _('Password changed')
        BIRTHDAY = 'birthday', _('Birthday changed')
        FIRST_NAME_CHANGED = 'first_name_changed', _('First name changed')
        LAST_NAME_CHANGED = 'last_name_changed', _('Last name changed')
        AVATAR_CHANGED = 'avatar', _('Avatar changed')

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=Activities)

    ip_address = models.GenericIPAddressField()
    device = models.ForeignKey('Device', on_delete=models.RESTRICT)

    date = models.DateTimeField(auto_now_add=True)
