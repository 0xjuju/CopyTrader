from django.db import models


class Token(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    transaction_hash = models.CharField(max_length=255, default="")
    token_in = models.CharField(max_length=255, default="")
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.token_in


class Wallet(models.Model):
    address = models.CharField(max_length=255, default="")
    token = models.ManyToManyField(Token)

    def __str__(self):
        return self.address

