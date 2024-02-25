from django.db import models


class Bot(models.Model):
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.address


class Gem(models.Model):
    name = models.CharField(max_length=255, default="")
    wallet = models.ManyToManyField("Wallet")
    contract_address = models.CharField(max_length=255, default="")
    date_added = models.DateTimeField(auto_now=True)
    event = models.CharField(max_length=255, default="")
    transaction_hash = models.CharField(max_length=255, default="")


class WalletFilter(models.Model):
    top_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_wallets = models.IntegerField(default=0)
    max_wallets = models.IntegerField(default=0)
    min_token_wins = models.IntegerField(default=1)  # Minimum number of profitable tokens wallet has bought


class Token(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    transaction_hash = models.CharField(max_length=255, default="")
    chain = models.CharField(max_length=255, default='')
    token_in = models.CharField(max_length=255, default="")
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    percent = models.FloatField(default=0)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.token_in


class Wallet(models.Model):
    address = models.CharField(max_length=255, default="")
    token = models.ManyToManyField(Token)
    human = models.BooleanField(default=False)

    def __str__(self):
        return self.address

    @property
    def total_transactions(self):
        total = self.transaction_set.count()
        return total

    @property
    def unique_tokens(self):
        total = self.token.count()
        return total



