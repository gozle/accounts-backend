from django.db import models


class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=100)
    message = models.TextField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
