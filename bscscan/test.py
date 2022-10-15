
from datetime import datetime
from bscscan.bscscan_api import BSCScan
from django.test import TestCase


class TestBscScan(TestCase):
    def setUp(self):
        self.api = BSCScan()

    def test_get_block_by_timestamp(self):
        t = int(1656288000000 / 1000)

        block = self.api.get_block_by_timestamp(t)

        s = datetime(year=2022, month=7, day=9)
        end = datetime(year=2022, month=7, day=14)







