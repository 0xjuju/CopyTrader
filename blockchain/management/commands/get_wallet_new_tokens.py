
from django.core.management.base import BaseCommand
from wallets.models import WalletFilter
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()

        for wallet in wallets:
            pass




