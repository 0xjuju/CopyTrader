from typing import Any, Union

from blockchain.models import Chain
from coingecko.models import Address
from pycoingecko import CoinGeckoAPI
from coingecko.models import GeckoToken


class GeckoClient:
    def __init__(self):
        self.client = CoinGeckoAPI()

    def get_coin_data(self, token_id: str) -> dict["str", Union[str, float, int]]:
        """
        token info from coingecko
        :param token_id: Token id name
        :return: Token data
        """
        return self.client.get_coins_markets(ids=token_id, vs_currency="usd")

    def get_asset_platforms(self):
        return self.client.get_asset_platforms()

    def get_coin_contract(self, token_id: str):
        """
        :param token_id: Token ID
        :return: dict: decimal_place, contract_address
        """

        return self.client.get_coin_by_id(token_id)

    def get_coins_list(self) -> list[dict[str, dict]]:
        return self.client.get_coins_list()

    def get_coins_markets(self, per_page=100, page=1) -> list[dict[str, Any]]:
        """

        :param per_page: hits per-page
        :param page: page number
        :return: list of tokens with market data
        """
        if per_page > 250:
            raise ValueError("250 max results per page")

        data = self.client.get_coins_markets(vs_currency="usd", page=page, price_change_percentage="7d")
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

    def get_market_charts_by_id(self, token_id: str, vs_currency="usd", days=30):
        return self.client.get_coin_market_chart_by_id(id=token_id, vs_currency=vs_currency, days=days)

    def parse_collection(self, collection: list[dict], percent_change_24h: float, percent_change_7d: float):
        """
        :param collection: list of token attributes
        :param percent_change_24h: 24 hour price change
        :param percent_change_7d: 7 day change
        :return: None, upload hits to database
        """

        chain_list = Chain.objects.values_list("name", flat=True)
        token_list = list()  # List of tokens meeting price-change requirements
        for token in collection:

            price_change_24hr = 0 if not token["price_change_percentage_24h"] else token["price_change_percentage_24h"]
            price_change_7d = 0 if not token["price_change_percentage_7d_in_currency"] else token["price_change_percentage_7d_in_currency"]

            if price_change_24hr >= percent_change_24h or price_change_7d >= percent_change_7d:

                token_id = token["id"]
                symbol = token["symbol"]
                name = token["name"]
                # market_cap = token["market_cap"]
                market_cap_rank = token["market_cap_rank"]
                # market_cap_change_24hr = f"{token['market_cap_change_24h']:,.2f}"

                if price_change_24hr or price_change_7d:

                    gecko_token, _ = GeckoToken.objects.get_or_create(name=name, symbol=symbol, token_id=token_id)
                    gecko_token.price_change_24h = price_change_24hr
                    gecko_token.price_change_7d = price_change_7d
                    gecko_token.rank = market_cap_rank
                    gecko_token.save()

                    if gecko_token.address_set.count() == 0:
                        contracts = self.get_coin_contract(token_id)
                        for contract_name in contracts["detail_platforms"]:

                            if contract_name:

                                contract = contracts["detail_platforms"][contract_name]["contract_address"]
                                decimals = contracts["detail_platforms"][contract_name]["decimal_place"]

                                if contract_name in chain_list and contract and decimals:
                                    new_address = Address.objects.create(
                                        contract=contract,
                                        chain=contract_name,
                                        decimals=decimals,
                                        token=gecko_token
                                    )
                                    new_address.save()

    def search_for_top_movers(self, pages: int, percent_change_24h: float, percent_change_7d: float, start_page: int = 0):

        """
        :param pages: Number of pages to paginate through
        :param percent_change_24h: 24 hour price change
        :param percent_change_7d: 7 dat price change
        :return:
        """

        # Reset fields
        GeckoToken.objects.all().update(price_change_24hr=0, price_change_7d=0)
        Address.objects.all().update(processed=False)

        for page in range(start_page, pages):
            collection = self.get_coins_markets(page=page+1)
            self.parse_collection(collection=collection, percent_change_24h=percent_change_24h,
                                  percent_change_7d=percent_change_7d)
            print(f"Done page: {page + 1}")














