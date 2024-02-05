from django.db import models
from users.validators.user import validate_name


class Profile(models.Model):
    first_name = models.CharField(max_length=100, validators=[validate_name])
    last_name = models.CharField(max_length=100, validators=[validate_name])
    avatar = None  # TODO
    birthday = models.DateField(null=True, blank=True)
