
from blockchain.alchemy import Webhook
from blockchain.models import AddressWebhook
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        w = Webhook()
        wallets = get_wallets()
        addresses = wallets.values_list("address")


        # w.replace_webhook_address_list()








