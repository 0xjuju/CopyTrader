import decouple

from blockchain.alchemy_webhooks import Webhook
from blockchain.models import Chain, AddressWebhook
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets


class Command(BaseCommand):
    def handle(self, *args, **options):
        chains = Chain.objects.values_list("name", flat=True)
        wallets = [i.address for i in get_wallets()]

        for chain in chains:
            new_webhook = Webhook().create_wallet_activity_webhook(
                chain=chain,
                webhook_url=decouple.config("WEBHOOK_WALLET_ACTIVITY_ENDPOINT"),
                webhook_type="ADDRESS_ACTIVITY",
                address_list=wallets
            )
            print(new_webhook)

            web_id = new_webhook["data"]["id"]
            webhook_model = AddressWebhook.objects.create(
                webhook_id=web_id,
                chain=chain,
                max_address=20
            )
            webhook_model.save()

