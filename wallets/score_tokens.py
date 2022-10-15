
from blockchain_explorer.blockchain_explorer import Explorer
import numpy as np
from wallets.models import *


class Score:
    def __init__(self, token):
        self.TOKEN = token

    def score_token(self):
        wallets = Wallet.objects.all()
        top_wallets = [i.transaction_set.count() for i in wallets]

        print(top_wallets)



