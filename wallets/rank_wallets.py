
from blockchain.identify_bots import Wallet
from django.db.models import Count
from wallets.models import Bot, WalletFilter, Wallet


def filter_wallets() -> None:
    wallets = get_wallets()
    chains = ["ethereum", "arbitrum-one", "polygon-pos"]
    for each in wallets:
        for chain in chains:
            wallet = Wallet(each.address, chain)
            is_bot = wallet.is_likely_bot()
            if is_bot is not None:
                if is_bot:  # Move wallet to known bot accounts model
                    Bot.objects.get_or_create(address=each.address)
                    each.delete()
                    break
                else:
                    pass


def get_wallets() -> list[Wallet]:
    filters = WalletFilter.objects.first()

    wallets = Wallet.objects\
        .annotate(token_count=Count('token'))\
        .filter(token_count__gte=filters.min_token_wins)\
        .order_by('-token_count')

    return wallets[0:filters.max_wallets]



