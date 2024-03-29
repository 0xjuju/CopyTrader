from django.db import models


class GeckoFilter(models.Model):
    name = models.CharField(max_length=255, default="")
    percent_change_24h = models.IntegerField(default=0)
    percent_change_7d = models.IntegerField(default=0)
    pages_to_parse = models.IntegerField(default=0)


class GeckoToken(models.Model):
    name = models.CharField(max_length=255, default="")
    symbol = models.CharField(max_length=255, default="")
    token_id = models.CharField(max_length=255, default="")
    date_added = models.DateTimeField(auto_now_add=True)
    price_change_24hr = models.FloatField(default=0)
    price_change_7d = models.FloatField(default=0)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Address(models.Model):
    contract = models.CharField(max_length=255, default="")
    chain = models.CharField(max_length=255, default="")
    token = models.ForeignKey(GeckoToken, on_delete=models.CASCADE, default=None)
    decimals = models.IntegerField(default=18)
    processed = models.BooleanField(default=False)





