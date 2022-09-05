from django.db import models


class Token(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Wallet(models.Model):
    address = models.CharField(max_length=255, default="")
    token = models.ManyToManyField(Token)

    def __str__(self):
        return self.address

