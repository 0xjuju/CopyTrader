from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Bot(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    @property
    def profit(self):
        total_in = Decimal(self.transaction_set.filter(transaction_type="sell").aggregate(total=Sum("amount_in")))
        total_out = Decimal(self.transaction_set.filter(transactiono_type="buy").aggregate(total=Sum("amount_out")))
        gas_used = Decimal(self.transaction_set.aggregate(total=Sum("gas_used")))

        profit_amount = total_in - total_out - gas_used
        profit_percent = (total_in - (total_out + gas_used)) / (total_out + gas_used) * 100

        return {
            "profit_amount": profit_amount,
            "profit_percent": profit_percent
        }


class Pool(models.Model):
    contract_address = models.CharField(max_length=255, default="")
    chain = models.CharField(max_length=255, default="")
    token1 = models.CharField(max_length=255, default="")
    token2 = models.CharField(max_length=255, default="")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, null=True, default=None)


class Transaction(models.Model):
    transaction_hash = models.CharField(max_length=255, default="")
    transaction_type = models.CharField(max_length=255, default="")
    amount_in = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_out = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gas_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)


