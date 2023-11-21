from django.core.management.base import BaseCommand
from blockchain_explorer.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()
        gecko_client = GeckoClient()

        chain_list = {
            # "ethereum",
            "arbitrum-one": list(),
            "polygon": list(),
            "binance-smart-chain": list(),
            "polygon-pos": list()
        }

        for page in range(2, 11):
            tokens = gecko_client.get_coins_markets(page=page)
            for token in tokens:
                token_id = token["id"]
                contracts = gecko_client.get_coin_contract(token_id)
                for name, contract in contracts.items():
                    if name in chain_list:
                        pass




