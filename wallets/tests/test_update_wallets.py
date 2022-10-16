
from django.test import TestCase
from wallets.models import Token
from wallets.tests.build_wallet_models import Build
from wallets.update_wallets import Updater, Wallet, Transaction


class TestUpdateWallets(TestCase):
    def setUp(self):
        Build().swap_pools()
        Build().tokens()
        Build().bots()

    def test_updater(self):
        token = Token.objects.filter(chain="ethereum").filter(pair="eth").get(name="agix")
        Updater().update(token)
        wallets = Wallet.objects.all()

        print(f"Total Wallets: {wallets.count()}")

        for wallet in wallets:
            print(wallet.address, f"Transactions: {wallet.transaction_set.count()}")




