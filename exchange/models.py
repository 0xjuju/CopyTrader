from django.db import models


class CoinbaseProduct(models.Model):
    base_currency = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.base_currency
