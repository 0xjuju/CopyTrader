from django.core.management.base import BaseCommand
from wallets.models import Token
from wallets.update_wallets import Updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        threshold = float(input("percent > "))
        Updater().update(percent_threshold=threshold)