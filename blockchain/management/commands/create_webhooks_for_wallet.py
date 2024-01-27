
from blockchain.alchemy_webhooks import Webhook
from blockchain.models import AddressWebhook
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        w = Webhook()
        wallets = get_wallets()
        addresses = wallets.values_list("address", flat=True)
        webhook = AddressWebhook.objects.all()

        # Each instance represents a different chain
        for each in webhook:
            chain = each.chain
            webhook_id = each.webhook_id
            w.replace_webhook_address_list(address_list=addresses, webhook_id=webhook_id)








