
from blockchain.alchemy import Webhook
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        w = Webhook()
        webhooks = w.get_all_webhooks()

        print(webhooks)





