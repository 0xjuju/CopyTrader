
from django.core.management.base import BaseCommand
from coingecko.coingecko_api import GeckoClient
from coingecko.models import GeckoFilter


class Command(BaseCommand):
    def handle(self, *args, **options):
        gf = GeckoFilter.objects.get(name="top_movers")

        api = GeckoClient()
        api.search_for_top_movers(pages=gf.pages_to_parse, percent_change_24h=gf.percent_change_24h,
                                  percent_change_7d=gf.percent_change_7d)



