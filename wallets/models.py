from django.db import models


class Bot(models.Model):
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.address


class WalletFilter(models.Model):
    top_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_wallets = models.IntegerField(default=0)
    max_wallets = models.IntegerField(default=0)
    min_token_wins = models.IntegerField(default=1)  # Minimum number of profitable tokens wallet has bought


class PairContract(models.Model):
    pair_options = (
        ("", "",),
        ("usdt", "usdt",),
        ("usdc", "usdc",),
        ("eth", "eth",),

        ("bnb", "bnb",),
        ("busd", "busd",),
        ("avax", "avax",),
        ("matic", "matic",),
        ("dai", "dai",),
        ("wbnb", "wbnb",),
    )

    chain_options = (
        ("", "",),
        ("ethereum", "ethereum",),
        ("arbitrum", "arbitrum",),
        ("polygon", "polygon",),
        ("bsc", "bsc",),
        ("avalanche", "avalanche",),
        ("solana", "solana",),
    )

    dex = models.CharField(max_length=25, default="")
    contract_address = models.CharField(max_length=255, default="")
    abi = models.TextField(default="")
    pair = models.CharField(max_length=15, default="", choices=pair_options)
    token = models.ForeignKey("Token", on_delete=models.CASCADE)
    chain = models.CharField(max_length=255, default="", choices=chain_options)

    def __str__(self):
        return self.dex


class PoolContract(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")
    abi = models.TextField(default="")
    version = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Token(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class OwnedToken(Token):

    date_added = models.DateTimeField(auto_now=True)
    owner_wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, default=None)
    balance = models.BigIntegerField( default=0)
    balance_increase = models.BooleanField(default=False)

    def __str__(self):
        return self.owner_wallet.address


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



