
from coingecko.coingecko_api import GeckoClient
from django.test import TestCase
from trading_bot.quant import *


class TestMonteCarlo(TestCase):
    def setUp(self):
        gecko_client = GeckoClient()
        volatile_charts = list()

        page = 20
        for _ in range(3):
            tokens = gecko_client.get_coins_markets(page=page)
            for token in tokens:
                print(token["name"])
                token_id = token["id"]
                price_chart = gecko_client.get_market_charts_by_id(token_id)
                prices = [i[1] for i in price_chart["prices"]]
                volatility = volatility_of_dataset(prices)
                print(volatility)
                print("-------------------------------------------------------------")

    def test_get_volatile_charts(self):
        pass












