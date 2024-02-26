
from wallets.rank_wallets import filter_wallets
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        filter_wallets()
        print("Filtering wallets done")


