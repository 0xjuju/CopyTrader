
from wallets.models import WalletFilter, Wallet


def get_wallets():
    filters = WalletFilter.objecs.first()

