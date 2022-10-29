from django.db import models


class Bot(models.Model):
    name = models.CharField(unique=True, max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class CoinbaseProduct(models.Model):
    base_currency = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.base_currency


class FactoryDex(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")
    abi = models.TextField()
    version = models.IntegerField(default=0)

    def __str__(self):
        return self.name



