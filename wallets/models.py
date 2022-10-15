from django.db import models


class Bot(models.Model):
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.address


class PoolContract(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")
    abi = models.TextField(max_length=255, default="")

    def __str__(self):
        return self.name


class PotentialGem(models.Model):
    name = models.CharField(max_length=255, default="")
    ticker = models.CharField(max_length=10, default="")
    contract_address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Token(models.Model):
    name = models.CharField(max_length=255, default="")
    pair = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")
    uniswap_contract = models.CharField(max_length=255, default="")
    uniswap_abi = models.TextField(default="")
    chain = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    transaction_hash = models.CharField(max_length=255, default="")
    token_in = models.CharField(max_length=255, default="")
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.token_in


class TargetWallet(models.Model):
    name = models.CharField(max_length=255, default="")
    chain = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=255, default="")
    contract = models.CharField(max_length=255, default="")
    abi = models.TextField(default="")
    balance = models.CharField(max_length=255, default="")
    run_tracker = models.BooleanField(default=False)

    def __str__(self):
        return self.address


class Wallet(models.Model):
    address = models.CharField(max_length=255, default="")
    token = models.ManyToManyField(Token)

    def __str__(self):
        return self.address

    @property
    def total_transactions(self):
        total = self.transaction_set.count()
        return total

