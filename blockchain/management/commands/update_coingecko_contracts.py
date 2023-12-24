
from blockchain.models import Chain
from django.core.management.base import BaseCommand
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken


class Command(BaseCommand):
    def handle(self, *args, **options):
        gecko_client = GeckoClient()
        existing_tokens = GeckoToken.objects.all()

        # Lists of token contract addresses belonging to their respective chains
        chain_list = Chain.objects.values_list("name", flat=True)
        print(chain_list)
        for page in range(1, 11):
            print(f" This page:::: {page}")
            tokens = gecko_client.get_coins_markets(page=page)
            for token in tokens:
                print(f"On Token {token['name']}")
                token_id = token["id"]
                symbol = token["symbol"]

                gecko_token, created = GeckoToken.objects.get_or_create(
                    token_id=token_id,
                )

                if created:
                    price_change_24hr = 0 if not token["price_change_percentage_24h"] else token[
                        "price_change_percentage_24h"]

                    price_change_7d = 0 if not token["price_change_percentage_7d_in_currency"] else token[
                        "price_change_percentage_7d_in_currency"]

                    market_cap_rank = token["market_cap_rank"]

                    gecko_token.price_change_24hr = price_change_24hr,
                    gecko_token.price_change_7d = price_change_7d,
                    gecko_token.rank = market_cap_rank
                    gecko_token.name = token["name"]
                    gecko_token.symbol = symbol

                gecko_token.save()

                if gecko_token.address_set.count() == 0:
                    print("Adding Contracts")
                    contracts = gecko_client.get_coin_contract(token_id)

                    for contract_name in contracts["detail_platforms"]:
                        if contract_name:
                            contract = contracts["detail_platforms"][contract_name]["contract_address"]
                            decimals = contracts["detail_platforms"][contract_name]["decimal_place"]
                            if contract_name in chain_list and contract and decimals:
                                print(contracts["detail_platforms"])
                                new_address = Address.objects.create(
                                    contract=contract,
                                    chain=contract_name,
                                    decimals=decimals,
                                    token=gecko_token
                                )
                                new_address.save()





