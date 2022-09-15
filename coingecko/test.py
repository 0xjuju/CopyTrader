from datetime import date

from coingecko.coingecko_api import GeckoClient
from django.test import TestCase


class TestCoingecko(TestCase):
    def setUp(self):
        self.api = GeckoClient()
        self.nexo_contract_address = "0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"

    def test_get_market_charts_by_contract(self):
        res = self.api.get_market_chart_by_contract(contract_address=self.nexo_contract_address, chain="ethereum")
        t = res["prices"][0][0]
