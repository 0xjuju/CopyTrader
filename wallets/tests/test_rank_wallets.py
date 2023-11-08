
from django.test import TestCase
from wallets.rank_wallets import get_wallets
from wallets.tests.build_wallet_models import Build


class TestRankWallet(TestCase):
    def setUp(self) -> None:
        Build.swap_pools()
        # Build.pair_contracts()
        Build.tokens()
        Build.wallets()
        Build.transactions()
        Build.wallet_filter()

    def test_get_wallets(self):
        wallets = get_wallets()




