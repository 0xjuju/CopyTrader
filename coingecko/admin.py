from django.contrib import admin
from .models import *


@admin.register(ONP)
class ONPAdmin(admin.ModelAdmin):
    list_display = ["name", "symbol", "token_id", "price_change_24hr", "price_change_7d", "rank", "date_added"]
