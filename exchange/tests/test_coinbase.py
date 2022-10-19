from collections import Counter

from django.test import TestCase
from exchange.coinbase import Coinbase
from exchange.models import CoinbaseProduct


class TestCoinbase(TestCase):
    def setUp(self):
        self.ex = Coinbase()

    def test_add_new_products_to_database(self):
        products = ["MKR", "MOVR", "BLOK", "CLY", "ROCO", "KUJI", "PHA", "STATE"]
        self.ex.add_new_products_to_database(products)
        newly_added_products = CoinbaseProduct.objects.values_list("base_currency", flat=True)
        self.assertEqual(Counter(products), Counter(newly_added_products))

    def test_check_for_new_products(self):
        products = self.ex.get_all_products()
        uploads = [CoinbaseProduct(base_currency=i["base_currency"]) for i in products]
        uploads += [
            CoinbaseProduct(base_currency="TEST1"),
            CoinbaseProduct(base_currency="TEST2"),
            CoinbaseProduct(base_currency="TEST3"),
            ]

        CoinbaseProduct.objects.bulk_create(uploads)
        new_products = self.ex.check_for_new_products()
        self.assertEqual(Counter(new_products), Counter(["TEST1", "TEST2", "TEST3"]))

    def test_get_all_products(self):
        products = self.ex.get_all_products()




