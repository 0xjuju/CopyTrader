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
