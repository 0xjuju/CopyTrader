
from blockchain.alchemy_webhooks import Webhook
import decouple
from django.test import TestCase


class TestAlchemyWebhooks(TestCase):
    def setUp(self) -> None:
        self.api = Webhook()
        self.ngrok_url = f"https://{decouple.config('NGROK_TEMP_HOST')}"

    def test_get_address_list_from_webhook(self):

        address_list = self.api.get_address_list_from_webhook("wh_mhgl1vaf8go3tzig")
        self.assertEqual(address_list["data"][0], '0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8')

    def test_replace_webhook_address_list(self):
        address_list = ["0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1"]
        self.api.replace_webhook_address_list("wh_mhgl1vaf8go3tzig", address_list=address_list)

    def test_create_swap_events_for_wallet_webhook(self):
        chain = "ethereum"

        r = self.api.create_swap_events_for_wallet_webhook(chain, self.ngrok_url,
                                                           "0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8")
        print(r)

    def test_delete_webhook(self):

        webhook_id = self.api.create_swap_events_for_wallet_webhook("ethereum", self.ngrok_url,
                                                                    ["0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8"])
        webhook_id = webhook_id["data"]["id"]
        self.api.delete_webhook(webhook_id)




