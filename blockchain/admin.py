from django.contrib import admin
from blockchain.models import *


@admin.register(ABI)
class ABIAdmin(admin.ModelAdmin):
    pass


@admin.register(AddressWebhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ["chain", "webhook_id", "max_address"]


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    pass


@admin.register(FactoryContract)
class FactoryContractAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "chain"]

