from decimal import Decimal

from decouple import config
from django.test import TestCase
from blockchain.etherscan import Etherscan


class TestEtherScanApi(TestCase):
    def setUp(self):
        self.test = Etherscan()

    def test_convert_balance_of_eth(self):
        t1 = self.test.convert_balance_to_eth(balance=Decimal(123456789), decimals=18)
        # self.assertAlmostEquals(t1, Decimal(1.23456789), places=4)

    def test_get_balance(self):
        test1 = self.test.get_eth_balance(config("MY_WALLET_ADDRESS"))
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], str, msg="Must be a String")

    def test_get_block_by_timestamp(self):
        from datetime import datetime
        d = datetime.now().timestamp()
        print(f"{int(d)}")

        block = self.test.get_block_by_timestamp(timestamp=f"{int(d)}")
        print(block)

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

        print(len(test1["result"]))

    def test_get_internal_transaction_list(self):
        test1 = self.test.get_internal_transaction_list(address=config("MY_WALLET_ADDRESS"))
        self.assertEqual(test1["status"], "1", msg=test1)
        self.assertEqual(test1["message"], "OK", msg=test1)
        self.assertIsInstance(test1["result"], list, msg=test1)
        self.assertIsInstance(test1["result"][0], dict, msg=test1)

    def test_get_erc20_transfer_events(self):
        test1 = self.test.get_internal_transaction_list(address=config("MY_WALLET_ADDRESS"))

    def test_get_internal_transaction_by_hash(self):
        test1 = self.test.get_internal_transaction_by_hash(
            transaction_hash="0xfc3f476eb589121f81629505b8eced85d83dfbb2615eee0173f6831963dbeb68")






