import requests

from webstuff.web_functions import request_get_data


class Coinbase:

    def __init__(self):
        self.BASE_URL = "https://api.exchange.coinbase.com/"

    def get_all_products(self):
        """
        :return: List available tokens available on Coinbase
        """
        headers = {"accept": "application/json"}
        path = "products"
        url = self.BASE_URL + path
        res = requests.get(url, headers=headers)
        return res.json()




