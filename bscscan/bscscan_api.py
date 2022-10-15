
from decouple import config
import requests


class BSCScan:
    def __init__(self):
        self.API_KEY = config("BSC_API_KEY")
        self.BASE_URL = "https://api.bscscan.com/api"

    def request_get_data(self, **kwargs):
        result = requests.get(url=self.BASE_URL, params=kwargs.get("params")).json()
        return result

    def get_block_by_timestamp(self, timestamp):
        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
            "apiKey": self.API_KEY,
        }

        return self.request_get_data(params=params)

