
import requests

from exchange.models import CoinbaseProduct


class Coinbase:

    def __init__(self):
        self.BASE_URL = "https://api.exchange.coinbase.com/"
        self.json_application_type = "application/json"

    @staticmethod
    def add_new_products_to_database(products: list[str]) -> None:
        """
        Add new tokens to database
        :param products: list of new tokens on Coinbase
        :return: None
        """
        products = [CoinbaseProduct(base_currency=i) for i in products]
        CoinbaseProduct.objects.bulk_create(products)

    def check_for_new_products(self) -> list[str]:
        """
        Find new product listings by comparing old record with current
        Send sms alert of new changes
        Update database with new entries
        """
        all_products = [i["base_currency"] for i in self.get_all_products()]
        old_products = CoinbaseProduct.objects.values_list("base_currency", flat=True)
        new_products = list(set(old_products).symmetric_difference(set(all_products)))

        # Update database
        if new_products:
            self.add_new_products_to_database(new_products)

        return new_products

    def get_all_products(self) -> list[dict]:
        """
        :return: List available tokens available on Coinbase
        """
        headers = {"accept": "application/json"}
        path = "products"
        url = self.BASE_URL + path
        res = requests.get(url, headers=headers)
        return res.json()

    def generate_signature(self, method, path):
        pass






