import random

from blockchain.identify_bots import *
from django.test import TestCase


class TestIdentifyBots(TestCase):
    def setUp(self):
        self.wallets = ["0x58781bec079B6485D1Be088422d7f9F35F8778CD",
            '0x65A8F07Bd9A8598E1b5B6C0a88F4779DBC077675', '0x13307b8854a95946b54A904100AFd0767a7a577b',
                        '0x0a6c69327d517568E6308F1E1CD2fD2B2b3cd4BF', '0x406cBFC2d391bEd42078138165465128b4E0CB06',
                        '0x111111115F51Ac6C670138c5EB879B5b071e22F0', '0xE4fF0913F86740E56E993D921b676AE6abdE479A',
                        '0x3bfaEf980D08Ca17bD5046cA7Bc6c692b92DE72c', '0xd0Be1fdED5d964619B92B3672C08c43305529bE0',
                        '0xa7D8e51b60c8A76Df85e7AF60cab5aB741e5bFeB', '0x7b9d4D8772b8705dDc7456Daf821c3022DDa0504',]

        self.user_wallet = Wallet("0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1", "ethereum")

    def test_average_time_between_transactions(self):

        swap_events = [
            {"timeStamp": datetime(month=2, day=1, year=2024, hour=8, minute=30).timestamp()},
            {"timeStamp": datetime(month=2, day=1, year=2024, hour=8, minute=45).timestamp()},
            {"timeStamp": datetime(month=2, day=1, year=2024, hour=8, minute=15).timestamp()},
        ]
        average = self.user_wallet._average_time_between_transactions(swap_events)
        self.assertEqual(average.seconds, 900)
        self.assertEqual(average.minutes(), 15)
        self.assertEqual(average.hours(), 0.25)

        user_txs = self.user_wallet.get_transactions_for_wallet()
        user_time = self.user_wallet._average_time_between_transactions(user_txs)

        bot1 = Wallet("0x65A8F07Bd9A8598E1b5B6C0a88F4779DBC077675", "ethereum")
        bot_txs = bot1.get_transactions_for_wallet()
        bot_time = bot1._average_time_between_transactions(bot_txs)

        # print(f"Human: {user_time.minutes()}") --> High average time between transactions (thousands of minutes)
        # print(f"Bot: {bot_time.minutes()}") --> Low time between transactions (a few minutes)

        for each in self.wallets:
            wallet = Wallet(each, "ethereum")
            transactions = wallet.get_transactions_for_wallet(10000)
            if transactions:
                average_time = wallet._average_time_between_transactions(transactions)
                print(f"{each}: Average time between txs is {average_time.minutes()} minutes")

    def test_get_transactions_for_wallet(self):
        swap_events = self.user_wallet.get_transactions_for_wallet()

        # Use random indexes to test that 'swap' is in each function name
        random_numbers = [random.randint(0, 10) for _ in range(5)]
        # for index in random_numbers:
        #     self.assertIn("swap", swap_events[index]["functionName"])

    def test_is_likely_bot(self):
        for each in self.wallets:
            wallet = Wallet(each, "ethereum")
            print(f"{each} Is bot? {wallet.is_likely_bot()}")






