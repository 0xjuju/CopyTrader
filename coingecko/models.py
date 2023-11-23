from django.db import models


class ONP(models.Model):
    name = models.CharField(max_length=255, default="")
    symbol = models.CharField(max_length=255, default="")
    token_id = models.CharField(unique=True, max_length=255, default="")
    date_added = models.DateTimeField(auto_now_add=True)
    price_change_24hr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_change_7d = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rank = models.IntegerField(default=0)


class GeckoToken(models.Model):
    name = models.CharField(max_length=255, default="")


class Address(models.Model):
    address = models.CharField(max_length=255, default="")
    chain = models.CharField(max_length=255, default="")
    token = models.ForeignKey(GeckoToken, on_delete=models.CASCADE, default=None)


