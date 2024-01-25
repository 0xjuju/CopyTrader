from datetime import timedelta, datetime
from decimal import Decimal
import time

from decouple import config
from django.test import TestCase
from blockchain.blockscsan import Blockscan


class TestBlockscan(TestCase):
    def setUp(self):
        self.test = Blockscan(chain="ethereum")
        self.test_polygon = Blockscan(chain="polygon-pos")

    def test_ping(self):
        chains = ["ethereum", "binance-smart-chain", "polygon-pos"]

        for chain in chains:
            ex = Blockscan(chain)
            balance = ex.get_eth_balance(config("MY_WALLET_ADDRESS"))
            self.assertEqual(balance["status"], "1")
            self.assertEqual(balance["message"], "OK")

    def test_convert_balance_of_eth(self):
        t1 = self.test.convert_balance_to_eth(balance=str(123456789), decimals=18)
        # self.assertAlmostEquals(t1, Decimal(1.23456789), places=4)

    def test_get_balance(self):
        test1 = self.test.get_eth_balance(config("MY_WALLET_ADDRESS"))
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], str, msg="Must be a String")

    def test_get_block_by_timestamp(self):
        t = int(1657670400000/1000)
        block = self.test.get_block_by_timestamp(timestamp=t, look_for_previous_block_if_error=True)
        self.assertEqual(block, 15130976)

    def test_get_contract_source_code(self):
        v = self.test_polygon.get_contract_source_code("0x229b1b6C23ff8953D663C4cBB519717e323a0a84")
        self.assertEqual(v["message"], "OK")
        self.assertEqual(v["status"], "1")

    def test_get_gas_price(self):
        gas = self.test.get_gas_price()
        self.assertEqual(gas["message"], "OK")
        self.assertEqual(gas["status"], "1")

    def test_get_multi_eth_balances(self):
        test_data = ["0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1", "0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8"]
        test1 = self.test.get_multi_eth_balances(test_data)
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], list, msg=test1)
        self.assertIsInstance(test1["result"][0], dict, msg=test1)
        self.assertNotEqual(test1["result"][0].get("account"), None)
        self.assertNotEqual(test1["result"][0].get("balance"), None)

        # test_data = [i for i in range(21)]
        # self.assertRaises(ValueError, self.test.get_multi_eth_balances(test_data))

    def test_get_normal_transaction_list(self):
        test1 = self.test.get_normal_transaction_list(address="0xb62132e35a6c13ee1ee0f84dc5d40bad8d815206",
                                                      start_block=15343400, end_block=15343589)
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], list, msg=test1)
        self.assertIsInstance(test1["result"][0], dict, msg=test1)

    def test_get_internal_transaction_list(self):
        test1 = self.test.get_internal_transaction_list(address=config("MY_WALLET_ADDRESS"))
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], list, msg=test1)
        self.assertIsInstance(test1["result"][0], dict, msg=test1)

    def test_get_erc20_transfer_events(self):
        test1 = self.test.get_internal_transaction_list(address=config("MY_WALLET_ADDRESS"))
        self.assertEqual(test1["status"], "1")
        self.assertEqual(test1["message"], "OK")

    def test_get_internal_transaction_by_hash(self):
        test1 = self.test.get_internal_transaction_by_hash(
            transaction_hash="0x70d518ce853677757d1a049b6599775be0b012c693ede6c9097b265c37a5ef88")






