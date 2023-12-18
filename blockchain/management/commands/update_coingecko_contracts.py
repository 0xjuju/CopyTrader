from django.core.management.base import BaseCommand
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken


class Command(BaseCommand):
    def handle(self, *args, **options):
        gecko_client = GeckoClient()
        existing_tokens = GeckoToken.objects.all()

        # Lists of token contract addresses belonging to their respective chains
        chain_list = {
            "ethereum": list(),
            "arbitrum-one": list(),
            "polygon": list(),
            "binance-smart-chain": list(),
            "polygon-pos": list(),
            "optimistic-ethereum": list(),
            "avalanche": list(),
            "solana": list(),
            "base": list(),
            "moonbeam": list(),
            "dogechain": list(),
        }

        for page in range(1, 11):
            print(f" This page:::: {page}")
            tokens = gecko_client.get_coins_markets(page=page)
            print(tokens)
            for token in tokens:
                token_id = token["id"]
                symbol = token["symbol"]

                if not existing_tokens.filter(token_id=token_id).exists():
                    price_change_24hr = 0 if not token["price_change_percentage_24h"] else token[
                        "price_change_percentage_24h"]
                    price_change_7d = 0 if not token["price_change_percentage_7d_in_currency"] else token[
                        "price_change_percentage_7d_in_currency"]
                    market_cap_rank = token["market_cap_rank"]

                    new_token = GeckoToken.objects.create(
                        name=token["name"],
                        token_id=token_id,
                        symbol=symbol,
                        price_change_24hr=price_change_24hr,
                        price_change_7d=price_change_7d,
                        rank=market_cap_rank
                    )
                    new_token.save()

                    contracts = gecko_client.get_coin_contract(token_id)
                    for contract_name in contracts:

                        if contract_name in chain_list:
                            new_address = Address.objects.create(
                                contract=contracts[contract_name]["contract_address"],
                                chain=contract_name,
                                decimals=contracts[contract_name]["decimal_places"],
                                token=new_token
                            )
                            new_address.save()





