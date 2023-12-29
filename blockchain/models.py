from django.db import models


class ABI(models.Model):
    abi_type = models.CharField(max_length=255, default="")
    text = models.TextField()

    def __str__(self):
        return self.abi_type


class Chain(models.Model):
    name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class FactoryContract(models.Model):
    chains = (
        ("ethereum", "ethereum", ),
        ("binance-smart-chain", "binance-smart-chain", ),
        ("polygon-pos", "polygon-pos", ),
        ("arbitrum-one", "arbitrum-one", ),
        ("base", "base", ),
        ("avalanche", "avalanche", ),
        ("solana", "solana", ),
    )
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")
    abi = models.TextField(default="")
    chain = models.TextField(default="")
    version = models.IntegerField(default=0)

