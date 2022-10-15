from django.core.management.base import BaseCommand
from wallets.models import Token, Wallet


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = Wallet.objects.all()
        print(f"Unique Wallets: {wallets.count()}")

        for wallet in wallets:
            print(wallet.address, f"Transactions: {wallet.transaction_set.values_list('transaction_hash', flat=True)}")
