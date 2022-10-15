
from django.test import TestCase
from wallets.models import *
from wallets.tests.build_wallet_models import Build


class TestWalletModels(TestCase):
    def setUp(self):
        Build.tokens()
        Build.wallets()
        Build.transactions()

    def test_wallet_total_transactions(self):
        wallet = Wallet.objects.first()
        self.assertEqual(wallet.total_transactions, 1)






