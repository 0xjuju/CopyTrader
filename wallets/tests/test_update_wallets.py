
from django.test import TestCase
from wallets.models import Token
from wallets.tests.build_wallet_models import Build
from wallets.update_wallets import Updater, Wallet, Transaction


class TestUpdateWallets(TestCase):
    def setUp(self):
        Build().swap_pools()
        Build().tokens()
        Build().bots()
        self.nexo = Token.objects.get(name="nexo")
        self.ethernity = Token.objects.get(name="ethernity")
        self.xwg = Token.objects.get(name="xwg")

    def test_updater(self):
        Updater().update(self.xwg)
        wallets = Wallet.objects.all()
        print(f"Total Wallets: {wallets.count()}")

        for wallet in wallets:
            print(wallet.address, f"Transactions: {wallet.transaction_set.count()}")




