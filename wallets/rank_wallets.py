from django.db.models import Count
from wallets.models import WalletFilter, Wallet


def get_wallets():
    filters = WalletFilter.objects.first()

    wallets = Wallet.objects\
        .annotate(token_count=Count('token'))\
        .filter(token_count__gte=filters.min_token_wins)\
        .order_by('-token_count')

    return wallets[0:filters.max_wallets]



