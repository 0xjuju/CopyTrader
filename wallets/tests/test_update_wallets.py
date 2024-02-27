from datetime import datetime

from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan
from coingecko.tests.build_coingecko_test_data import BuildGeckoModel
from django.test import TestCase
from wallets.models import Token
from wallets.tests.build_wallet_models import Build
from wallets.update_wallets import Updater, Wallet


class TestUpdateWallets(TestCase):
    def setUp(self):
        Build.tokens()
        Build.bots()
        Build.abi()
        BuildGeckoModel.build_tokens()
        self.blockchain = Blockchain("ethereum")

    def test_create_block_range(self):
        # duration = 7
        # timestamp = 1657857600  # 7/15/2022 00:00:00
        # explorer = Blockscan(chain="ethereum")
        #
        # from_block, to_block = Updater.create_block_range(
        #     duration=duration, timestamp=timestamp, explorer=explorer
        # )
        #
        # self.assertEqual(from_block, 15144985)
        # self.assertEqual(to_block, 15170801)

        timestamp = 1701993600000 / 1000.
        dt = datetime.fromtimestamp(timestamp)
        print(dt)

    def test_determine_price_breakouts(self):
        percent_threshold = 30

        diffs = [
            [-6., 45, 50],
            [-20, -47, -6],
            [150, 10, -75],
        ]

        # Real timestamp irrelevant for this testcase
        timestamps = [12222, 13333, 14444]

        breakouts = Updater.determine_price_breakouts(diffs=diffs, timestamps=timestamps,
                                                      percent_threshold=percent_threshold)

        self.assertEqual(breakouts[0].day, 3)
        self.assertEqual(breakouts[0].largest_price_move, 50)
        self.assertEqual(breakouts[1].day, 1)
        self.assertEqual(breakouts[1].largest_price_move, 150)

    def test_get_prices(self):
        contract_address = "0x155f0DD04424939368972f4e1838687d6a831151"
        chain = "arbitrum_one"
        timestamps, prices = Updater.get_prices_data(contract_address=contract_address, chain=chain)
        self.assertGreater(len(timestamps), 100)
        self.assertGreater(len(prices), 100)
        self.assertEqual(type(timestamps[0]), int)

    def test_get_transactions(self):
        transactions = Updater.get_transactions(
            from_block=19299160,
            to_block=19299760,
            contract="0xd084944d3c05cd115c09d072b9f44ba3e0e45921",
            blockchain=self.blockchain
        )

        for each in transactions:
            event = self.blockchain.get_event(each["data"], each["topics"], "Any")
            print(event.event, event.logs)

        self.assertEqual(transactions[0]["address"], "0xd084944d3c05CD115C09d072B9F44bA3E0E45921")

    def test_map_buyers_sellers(self):
        transactions = Updater.get_transactions(
            from_block=19299160,
            to_block=19299760,
            contract="0xd084944d3c05cd115c09d072b9f44ba3e0e45921",
            blockchain=self.blockchain
        )

        buyers, sellers = Updater().map_buyers_and_sellers(self.blockchain, transactions, [])

        print(buyers)

    def test_updater(self):
        token = Token.objects.get(name="FRONT")
        Updater().update(percent_threshold=1.40)
        wallets = Wallet.objects.all()

        print(f"Total Wallets: {wallets.count()}")

        for wallet in wallets:
            print(wallet.address, f"Transactions: {wallet.transaction_set.count()} >>>>"
                                  f" {wallet.transaction_set.values_list('transaction_hash', flat=True)}")




