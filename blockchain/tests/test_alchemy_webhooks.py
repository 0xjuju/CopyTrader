
from blockchain.alchemy_webhooks import Webhook
from django.test import TestCase


class TestAlchemyWebhooks(TestCase):
    def setUp(self) -> None:
        self.api = Webhook()

    def test_get_address_list_from_webhook(self):

        address_list = self.api.get_address_list_from_webhook("wh_mhgl1vaf8go3tzig")
        self.assertEqual(address_list["data"][0], '0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8')

    def test_replace_webhook_address_list(self):
        address_list = ["0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8"]
        self.api.replace_webhook_address_list("wh_mhgl1vaf8go3tzig", address_list)




