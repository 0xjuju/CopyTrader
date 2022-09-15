
from pycoingecko import CoinGeckoAPI


class GeckoClient:
    def __init__(self):
        self.client = CoinGeckoAPI()

    def get_market_chart_by_contract(self, *, contract_address: str, chain: str, days: int = 100, currency="usd"):

        return self.client.get_coin_market_chart_from_contract_address_by_id(id=chain,
                                                                             contract_address=contract_address,
                                                                             vs_currency=currency, days=days)







