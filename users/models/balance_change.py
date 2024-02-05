import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BalanceChange(models.Model):
    class BalanceChangeTypes(models.TextChoices):
        DEPOSIT = 'deposit', _('Deposit')
        TRANSFER = 'transfer', _('Transfer')
        PAYMENT = 'payment', _('Payment')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='balance_changes')

    type = models.CharField(max_length=20, choices=BalanceChangeTypes)
    amount = models.FloatField()
    source = models.CharField(max_length=50, blank=True, null=True)

    complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
