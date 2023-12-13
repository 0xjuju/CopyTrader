from django.contrib import admin
from .models import *


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["token", "chain", "contract"]

@admin.register(GeckoToken)
class GeckoTokenAdmin(admin.ModelAdmin):
    list_display = ["name", "token_id"]
    search_fields = ["name"]
