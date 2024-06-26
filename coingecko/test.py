from datetime import datetime

from coingecko.coingecko_api import GeckoClient
from django.test import TestCase


class TestCoingecko(TestCase):
    def setUp(self):
        self.api = GeckoClient()
        self.nexo_contract_address = "0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"

    def test_get_coin_data(self):
        data = self.api.get_coin_data("sidus")
        self.assertEqual(data[0]["name"], "Sidus")

    def test_get_asset_platforms(self):
        v = self.api.get_asset_platforms()

    def test_get_coin_contract(self):
        data = self.api.get_coin_contract("poof-token")
        self.assertEqual(data["symbol"], "poof")

    def test_get_coins_list(self):
        tokens = self.api.get_coins_list()

    def test_get_coins_markets(self):
        res = self.api.get_coins_markets(page=2)

    def test_get_market_charts_by_contract(self):
        res = self.api.get_market_chart_by_contract(contract_address=self.nexo_contract_address, days=100,
                                                    chain="ethereum")

        t = res["prices"]
        print(t)
        # res = self.api.get_market_chart_by_contract(contract_address="0x6b23c89196deb721e6fd9726e6c76e4810a464bc", chain="bsc")

    def test_get_market_charts_by_id(self):
        charts = self.api.get_market_charts_by_id(token_id="shido")

    def test_parse_collection(self):
        collection = self.api.get_coins_markets(page=4)

        self.api.parse_collection(collection=collection, percent_change_24h=40, percent_change_7d=70)
        from .models import GeckoToken
        tokens = GeckoToken.objects.all()






