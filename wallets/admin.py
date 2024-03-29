
from django.contrib import admin
from wallets.models import *


@admin.register(WalletFilter)
class FilterParamsAdmin(admin.ModelAdmin):
    list_display = ("top_percent", "min_wallets", "max_wallets", "min_token_wins")


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("name", "address", )


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    pass


@admin.register(Gem)
class GemAdmin(admin.ModelAdmin):
    list_display = ["name", "contract_address", "date_added"]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    search_fields = ("address", )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = ("wallet", )
    list_display = ("transaction_hash", "timestamp", "token_in", "chain", "amount", "percent", "wallet", )



