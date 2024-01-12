from django.core.management.base import BaseCommand
from coingecko.coingecko_api import GeckoClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        api = GeckoClient()
        api.search_for_top_movers(pages=10, percent_change_24h=75, percent_change_7d=75)



