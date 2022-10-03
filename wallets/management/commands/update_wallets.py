from django.core.management.base import BaseCommand
from wallets.models import Token
from wallets.update_wallets import updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = input("Token Name > ")
        print("starting...")
        updater(token=Token.objects.get(name=token))

