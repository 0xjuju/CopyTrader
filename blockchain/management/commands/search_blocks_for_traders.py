from django.core.management.base import BaseCommand
from blockchain.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from coingecko.models import GeckoToken
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()
        gecko_client = GeckoClient()

        # Lists of token contract addresses belonging to their respective chains
        chain_list = {
            # "ethereum",
            "arbitrum-one": list(),
              "polygon": list(),
            "binance-smart-chain": list(),
            "polygon-pos": list()
        }

        for page in range(1, 11):
            print(f" This page:::: {page}")
            tokens = gecko_client.get_coins_markets(page=page)
            print(tokens)
            for token in tokens:
                token_id = token["id"]
                print(token_id)

                contracts = gecko_client.get_coin_contract(token_id)
                for name, contract in contracts.items():

                    if name in chain_list:
                        chain_list[name].append(contract)

