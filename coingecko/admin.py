from django.contrib import admin
from .models import *


@admin.register(ONP)
class ONPAdmin(admin.ModelAdmin):
    list_display = ["name", "symbol", "token_id", "price_change", "date_added"]
