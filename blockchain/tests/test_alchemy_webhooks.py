
from blockchain.alchemy import Webhook
from django.test import TestCase


class TestAlchemyWebhooks(TestCase):
    def setUp(self) -> None:
        self.api = Webhook()

    def test_get_address_list_from_webhook(self):

        address_list = self.api.get_address_list_from_webhook("wh_mhgl1vaf8go3tzig")
        print(address_list.json())





