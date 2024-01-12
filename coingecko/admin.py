from django.contrib import admin
from .models import *


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["token","token_name", "chain", "contract"]
    search_fields = ["token"]

    def token_name(self, obj):
        return obj.token.name


@admin.register(GeckoToken)
class GeckoTokenAdmin(admin.ModelAdmin):
    list_display = ["name", "token_id", "symbol", "price_change_24hr", "price_change_7d", "rank", "date_added"]
    search_fields = ["name"]
