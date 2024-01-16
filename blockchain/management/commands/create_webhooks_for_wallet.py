
from blockchain.alchemy import Webhook
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        w = Webhook()

        active_webhooks = w.get_all_webhooks()






