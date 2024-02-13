from django.db import models


class Security(models.Model):
    recovery_email = models.EmailField()
