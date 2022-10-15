from django.core.management.base import BaseCommand
from wallets.models import Token
from wallets.update_wallets import Updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = input("Token Name > ")
        print("starting...")
        Updater().update(token=Token.objects.get(name=token))

