
from django.test import TestCase
from wallets.models import *
from wallets.score_tokens import Score
from wallets.tests.build_wallet_models import Build


class TestScoreTokens(TestCase):
    def setUp(self):
        Build.tokens()
        Build.wallets()
        Build.potential_gems()
        Build.transactions()
        token = PotentialGem.objects.get(name="nexo")
        self.score = Score(token=token)

    def test_score(self):
        s = self.score.score_token()









