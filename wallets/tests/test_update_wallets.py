
from blockchain_explorer.blockchain_explorer import Explorer
from blockchain_explorer.blockscsan import Blockscan
from django.test import TestCase
from wallets.models import Token
from wallets.tests.build_wallet_models import Build
from wallets.update_wallets import Updater, Wallet


class TestUpdateWallets(TestCase):
    def setUp(self):
        Build.swap_pools()
        Build.tokens()
        Build.pair_contracts()
        Build.bots()

    def test_create_block_range(self):
        duration = 7
        timestamp = 1657857600  # 7/15/2022 00:00:00
        explorer = Blockscan(chain="ethereum")

        from_block, to_block = Updater.create_block_range(
            duration=duration, timestamp=timestamp, explorer=explorer
        )

        self.assertEqual(from_block, 15144985)
        self.assertEqual(to_block, 15170801)

    def test_determine_price_breakouts(self):
        percent_threshold = 1.3

        diffs = [
            (0.94, 1.45, 1.50),
            (0.20, 0.53, 0.94),
            (2.5, 1.10, 0.25),
        ]

        # Real timestamp irrelevant for this testcase
        timestamps = [12345, 12345, 12345]

        breakouts = Updater.determine_price_breakouts(diffs=diffs, timestamps=timestamps,
                                                      percent_threshold=percent_threshold)
        self.assertEqual(breakouts[0][0], 3)
        self.assertEqual(breakouts[0][2], 50)
        self.assertEqual(breakouts[1][0], 1)
        self.assertEqual(breakouts[1][2], 150)

    def test_get_prices(self):
        contract_address = "0x155f0DD04424939368972f4e1838687d6a831151"
        chain = "arbitrum_one"
        timestamps, prices = Updater.get_prices_data(contract_address=contract_address, chain=chain)
        self.assertGreater(len(timestamps), 100)
        self.assertGreater(len(prices), 100)
        self.assertEqual(type(timestamps[0]), int)

    def test_get_transactions(self):
        from_block = 15144985
        to_block = 15170801
        token = Token.objects.get(name="nexo")
        contract = token.paircontract_set.first()
        blockchain = Explorer(chain="ethereum")
        txs = Updater().get_transactions(
            from_block=from_block,
            to_block=to_block,
            contract=contract,
            blockchain=blockchain,
        )
        hashes = [i["transactionHash"].hex() for i in txs]
        self.assertIn("0xec8103a1af202c616c57a396f87d5fd94ede03c643bdab42b6b47378c117f4b3", hashes)

    def test_updater(self):
        token = Token.objects.get(name="FRONT")
        Updater().update(token, percent_threshold=1.40)
        wallets = Wallet.objects.all()

        print(f"Total Wallets: {wallets.count()}")

        for wallet in wallets:
            print(wallet.address, f"Transactions: {wallet.transaction_set.count()} >>>>"
                                  f" {wallet.transaction_set.values_list('transaction_hash', flat=True)}")




