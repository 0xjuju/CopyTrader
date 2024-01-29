
from coingecko.coingecko_api import GeckoClient
from django.test import TestCase
from trading_bot.quant import *
from trading_bot.trading_bot import Bot


class TestMonteCarlo(TestCase):
    def setUp(self):
        gecko_client = GeckoClient()
        self.eth_bot = Bot("ethereum", "24hr")

        volatile_sets = list()
        non_volatile_sets = list()

        page = 20
        for _ in range(3):
            tokens = gecko_client.get_coins_markets(page=page)
            for token in tokens:
                token_id = token["id"]
                price_chart = gecko_client.get_market_charts_by_id(token_id)
                prices = [i[1] for i in price_chart["prices"]]
                volatile_set = self.eth_bot.extract_volatile_charts(dataset=prices, depth=30, variation_percent=5,
                                                                    vol_threshold=15)
                if volatile_set:
                    print(f"Volatile > {token['name']}")
                    volatile_sets.append(volatile_set)
                else:
                    print(f"Not* volatile {token['name']}")
                    non_volatile_sets.append(
                        prices[-30:]
                    )

    def test_get_volatile_charts(self):
        pass












