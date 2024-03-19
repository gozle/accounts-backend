from django.db import models


class Device(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=100)
    browser = models.CharField(max_length=20)
    os = models.CharField(max_length=20)
    fingerprint = models.CharField(max_length=500)
