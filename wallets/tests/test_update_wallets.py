
from django.test import TestCase
from wallets.models import Token
from wallets.tests.build_wallet_models import Build
from wallets.update_wallets import updater


class TestUpdateWallets(TestCase):
    def setUp(self):
        Build().swap_pools()
        Build().tokens()
        Build().bots()
        self.nexo = Token.objects.get(name="nexo")

    def test_updater(self):
        updater(self.nexo)


