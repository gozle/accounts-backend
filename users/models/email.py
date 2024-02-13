import pytz
from django.db import models


class Email(models.Model):
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_created_at(self, timezone='UTC'):
        return self.created_at.astimezone(tz=pytz.timezone(timezone))
