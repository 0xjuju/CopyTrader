

from django.test import TestCase
from exchange.coinbase import Coinbase


class TestCoinbase(TestCase):
    def setUp(self):
        self.ex = Coinbase()

    def test_get_all_products(self):
        products = self.ex.get_all_products()
        for each in products:
            if each["base_currency"] == "APT":
                print(each)



