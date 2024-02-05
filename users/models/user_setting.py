from django.db import models
from django.utils.translation import gettext_lazy as _


class UserSetting(models.Model):
    class Languages(models.TextChoices):
        ENGLISH = "EN", _("English")
        RUSSIAN = "RU", _("Russian")
        TURKMEN = "TK", _("Turkmen")

    class Themes(models.TextChoices):
        LIGHT = 'light', _('Light')
        DARK = 'dark', _('Dark')

    class TwoFactorAuthTypes(models.TextChoices):
        PASSWORD = 'password', _('Password')
        NONE = 'none', _('None')

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="settings")
    city = models.ForeignKey('City', blank=True, null=True, on_delete=models.SET_NULL)
    theme = models.CharField(max_length=10, choices=Themes, default=Themes.LIGHT)
    language = models.CharField(max_length=10, choices=Languages, default=Languages.TURKMEN)

    two_factor_auth = models.CharField(max_length=20, blank=True,
                                       choices=TwoFactorAuthTypes,
                                       default=TwoFactorAuthTypes.NONE)
