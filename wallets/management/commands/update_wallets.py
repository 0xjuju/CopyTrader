from django.core.management.base import BaseCommand
from wallets.models import Token
from wallets.update_wallets import Updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        threshold = float(input("percent > "))
        threshold = (threshold / 100) + 1
        print(threshold)
        print("starting...")
        Updater().update(percent_threshold=threshold)
