from django.core.management.base import BaseCommand
from wallets.models import Token
from wallets.update_wallets import Updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = input("Token Name > ")
        chain = input("Chain > ")
        pair = input("Pair > ")
        thresshold = float(input("percent > "))
        thresshold = (thresshold / 100) + 1
        print(thresshold)
        print("starting...")
        Updater().update(token=Token.objects.filter(chain=chain).filter(pair=pair).get(name=token),
                         percent_thresshold=thresshold)

