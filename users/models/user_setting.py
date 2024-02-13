from django.db import models
from django.utils.translation import gettext_lazy as _


class UserSettings(models.Model):
    class Themes(models.TextChoices):
        DARK = "dark", _("Dark")
        LIGHT = "light", _("Light")

    class Languages(models.TextChoices):
        ENGLISH = "EN", _("English")
        RUSSIAN = "RU", _("Russian")
        TURKMEN = "TK", _("Turkmen")

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(max_length=10, choices=Themes, default=Themes.LIGHT)
    language = models.CharField(max_length=10, choices=Languages, default=Languages.TURKMEN)
    two_factor_auth = models.BooleanField(default=False)
