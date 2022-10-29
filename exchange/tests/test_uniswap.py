
from decouple import config
from django.test import TestCase

from exchange.tests.build_exchage_models import Build as BuildExchangeModels
from exchange.models import Bot
from exchange.uniswap import UniswapAPI
from wallets.tests.build_wallet_models import Build as BuildWalletModels


class TestUniswap(TestCase):
    def setUp(self):
        BuildWalletModels.swap_pools()
        BuildExchangeModels.factory_dex()
        BuildExchangeModels.bots()
        bot1 = Bot.objects.get(name="BOT1")
        self.uni = UniswapAPI(chain="ethereum", address=bot1.address, private_key=config(bot1.name), use_testnet=True)
        self.eth = "0x0000000000000000000000000000000000000000"
        self.weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        self.bat = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
        self.usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    def test_get_router_contract(self):
        contract = self.uni.get_router_contract()


    def test_Swap_token_for_eth(self):
        tx = self.uni.swap_token_for_eth(token_address=self.usdc, amount_out=10)
        print(tx)





