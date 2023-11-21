import time

from pycoingecko import CoinGeckoAPI
from .models import ONP


class GeckoClient:
    def __init__(self):
        self.client = CoinGeckoAPI()

    def get_asset_platforms(self):
        return self.client.get_asset_platforms()

    def get_coin_contract(self, token_id: str):
        return self.client.get_coin_by_id(token_id)

    def get_coins_list(self):
        return self.client.get_coins_list()

    def get_coins_markets(self, per_page=100, page=1):
        if per_page > 250:
            raise ValueError("250 max results per page")

        data = self.client.get_coins_markets(vs_currency="usd", page=page)
        if data:
            return data


    def get_market_chart_by_contract(self, *, contract_address: str, chain: str, days: int = 100, currency="usd"):
        chain_map = {
            "bsc": "binance-smart-chain",
            "polygon": "polygon-pos",
            "arbitrum_one": "arbitrum-one",
            "arbitrum_nova": "arbitrum-nova",
            "dogechain": "dogechain",
        }
        return self.client.get_coin_market_chart_from_contract_address_by_id(id=chain_map.get(chain, chain),
                                                                                 contract_address=contract_address,
                                                                                 vs_currency=currency, days=days)
    def parse_collection(self, collection: list[dict], percent_change: float):
        """
        :param collection: list of token attributes
        :param percent_change: 24 hour price change
        :return: None, upload hits to database
        """

        token_list = list()  # List of tokens meeting price-change requirements
        for token in collection:
            price_change_24hr = token["price_change_percentage_24h"]
            print(token["market_cap_rank"])

            if price_change_24hr is not None and price_change_24hr >= percent_change:
                token_id = token["id"]
                symbol = token["symbol"]
                name = token["name"]
                market_cap = token["market_cap"]
                market_cap_rank = token["market_cap_rank"]
                market_cap_change_24hr = f"{token['market_cap_change_24h']:,.2f}"

                if not ONP.objects.filter(token_id=token_id).exists():

                    token_list.append(
                        ONP(
                            name=name,
                            symbol=symbol,
                            token_id=token_id,
                            price_change=price_change_24hr,
                            rank=market_cap_rank
                        )
                    )

        ONP.objects.bulk_create(token_list)

    def search_for_top_movers(self, pages:int):
        """
        :param pages: Number of pages to search (250 hits per page)
        :return:
        """
        for page in range(pages):
            print(f"searching in Page {page + 1}")
            collection = self.get_coins_markets(page=page+1)
            self.parse_collection(collection=collection, percent_change=50)














