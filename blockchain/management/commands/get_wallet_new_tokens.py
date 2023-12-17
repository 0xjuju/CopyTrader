
from blockchain.blockchain_explorer import Explorer
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()

        for wallet in wallets:
            held_tokens = wallet.owned_token_set.all()
            for token in held_tokens:

                pass




