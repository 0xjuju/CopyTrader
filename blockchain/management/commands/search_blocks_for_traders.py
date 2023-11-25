from django.core.management.base import BaseCommand
from blockchain.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        gecko_client = GeckoClient()
        chain_list = [
            "arbitrum-one",
            "polygon-pos",
            "polygon",
            "binance-smart-chain",
        ]

        for chain in chain_list:
            exp = Explorer(chain)
            block_range = exp.get_last_n_blocks(50)






