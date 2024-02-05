import pytz
from django.db import models


# email model class for user
class Email(models.Model):
    user_id = models.UUIDField()
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    def get_created_at(self, timezone='UTC'):
        return self.created_at.astimezone(tz=pytz.timezone(timezone))
