from blockchain.alchemy_webhooks import Webhook
from blockchain.models import Chain, AddressWebhook
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        chains = Chain.objects.all()
        wallets = get_wallets().values_list("address", flat=True)

        for chain in chains:
            new_webhook = Webhook().create_wallet_activity_webhook(
                chain=chain,
                webhook_type="ADDRESS_ACTIVITY",
                address_list=wallets
            )

            web_id = new_webhook["id"]
            webhook_model = AddressWebhook.objects.create(
                webhook_id=web_id,
                chain=chain,
                max_address=20
            )
            webhook_model.save()

