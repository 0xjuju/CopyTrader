from django.contrib import admin
from .models import *


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["token", "chain", "contract"]

@admin.register(GeckoToken)
class GeckoTokenAdmin(admin.ModelAdmin):
    list_display = ["name", "token_id"]
    search_fields = ["name"]

@admin.register(ONP)
class ONPAdmin(admin.ModelAdmin):
    list_display = ["name", "symbol", "token_id", "price_change_24hr", "price_change_7d", "rank", "date_added"]
