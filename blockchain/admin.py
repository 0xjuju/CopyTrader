from django.contrib import admin
from blockchain.models import *


@admin.register(ABI)
class ABIAdmin(admin.ModelAdmin):
    pass
