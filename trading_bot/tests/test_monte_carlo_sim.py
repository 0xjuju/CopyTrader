
from coingecko.coingecko_api import GeckoClient
from django.test import TestCase


class TestMonteCarlo(TestCase):
    def setUp(self):
        gecko_client = GeckoClient()
        charts = gecko_client.









