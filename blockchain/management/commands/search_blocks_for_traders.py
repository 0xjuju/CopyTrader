from django.core.management.base import BaseCommand
from blockchain.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()
        gecko_client = GeckoClient()
        existing_tokens = GeckoToken.objects.all()



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

                if not existing_tokens.filter(token_id=token_id).exists():
                    new_token = GeckoToken.objects.create(
                        name=token["name"],
                        token_id=token_id
                    )
                    new_token.save()
                    contracts = gecko_client.get_coin_contract(token_id)
                    for chain, contract in contracts.items():
                        if chain in chain_list:
                            new_address = Address.objects.create(
                                contract=contract,
                                chain=chain,
                                token=new_token
                            )
                            new_address.save()





