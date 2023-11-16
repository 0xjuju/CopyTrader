from django.core.management.base import BaseCommand
from blockchain_explorer.blockchain_explorer import Explorer
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()

        chain_list = ["eth"]

        for chain in chain_list:
            ex = Explorer(chain)

            for wallet in wallets:
                address = ex.convert_to_checksum_address(address=wallet.address)










