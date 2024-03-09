from datetime import datetime, timedelta

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan
from blockchain.tests.build_test_data import build_factory_contracts
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
        build_factory_contracts()

        self.blockchain = Blockchain("ethereum")
        self.blockscan = Blockscan("ethereum")

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
            contract="0xa914a9b9e03b6af84f9c6bd2e0e8d27d405695db",
            blockchain=self.blockchain
        )

        self.assertEqual(transactions[0]["transactionHash"].hex(),
                         "0x5207e97e0c13459e11d8a55ee037a52bb85123724c42caaf4f501e6eb8f3d93f")

    def test_map_buyers_sellers(self):
        transactions = Updater.get_transactions(
            from_block=19285160,
            to_block=19299760,
            contract="0xa914a9b9e03b6af84f9c6bd2e0e8d27d405695db",
            blockchain=self.blockchain
        )

        buyers, sellers = Updater().map_buyers_and_sellers(self.blockchain, transactions, [])
        buy_hashes = ["0x75230f318cecc89bf9c9f6643b9e43f3a8be72d96571f23011e2627718c29b98",
                      "0x297db8820ba1489b122a5443c9d9732c6ec25dc83952fa7c4484ef740de9eae6",
                      "0xb25d0259cc9052b3b567ed4ae7f1ff0c3d9a98198330207c0c7c334a139b4008",
                      "0x47fe44e16e86beefbddca8377bf28cddc9782a5608c5dfec6c46a8617d8df489"]

        sell_hashes = ["0x5207e97e0c13459e11d8a55ee037a52bb85123724c42caaf4f501e6eb8f3d93f"]

        for address, each in buyers.items():
            self.assertEqual(each[0].side, "buy")
            self.assertIn(each[0].transaction["transactionHash"].hex(), buy_hashes)

        for address, each in sellers.items():
            self.assertEqual(each[0].side, "sell")
            self.assertIn(each[0].transaction["transactionHash"].hex(), sell_hashes)

    def test_updater(self):
        percentage = 50
        print(f"Looking for Coingecko Tokens on Ethereum, that has increased by at least {percentage}%")

        pools = dict()

        # List of token contracts to loop through

        class Contract:
            def __init__(self, name, address, chain):
                self.name = name
                self.address = address
                self.chain = chain

        contracts = [
            # Contract(name="Dvision Network", address="0xF29f568F971C043Df7079A3121e9DE616b8998a3"),
            Contract(name="Manifold Finance", address="0xd084944d3c05cd115c09d072b9f44ba3e0e45921", chain="ethereum"),
        ]

        print(f"Here is the {len(contracts)} Coingecko token contact(s) we are looping through: {contracts}")

        for contract in contracts:
            print(f"Name of Token we are analyzing is {contract.name}")

            print("Converting token contract to Checksum Address...")
            token_contract = self.blockchain.checksum_address(contract.address)
            print(f"Token changed from {contract.address} to {token_contract}")

            print(f" > Now getting all pools that contain {contract.name}")
            pools.update(Updater.get_dex_pairs(self.blockchain, token_contract))

            print(" > Get contract address for each pool...")
            pool_contracts = Updater.get_pool_contracts(pools, contract)
            print(f"{len(pool_contracts)} contracts: {pool_contracts}")

            print(f" > Getting timestamps and prices from Coingecko for the given contract...\n")
            timestamps, prices = Updater.get_prices_data(contract.address, contract.chain)
            print(f" > {len(prices)} results. In the format: (Timestamp, Price)\n")
            print(list(zip([f"{datetime.fromtimestamp(i)}" for i in timestamps], prices)))

            print(" > Calculate percentage difference of each days' price relative to the next day, 3rd, and 7th\n")
            diffs = percent_difference_from_dataset(prices)
            print([f"({i[0]:,.2f}% 1 day, {i[1]:,.2f}% 3 days, {i[2]:,.2f}%) 7 days" for i in diffs])

            print(f"\n > Determine which days have prices that increased by at least {percentage}%\n")
            price_breakouts = Updater.determine_price_breakouts(diffs, timestamps, percentage)

            print("Looping through each day, creating a block range before price breakout started\n")
            for index, coingecko_breakout in enumerate(price_breakouts):
                duration = coingecko_breakout.day
                timestamp = coingecko_breakout.timestamp
                percentage = coingecko_breakout.largest_price_move

                block_data = Updater.create_block_range(duration, timestamp, self.blockscan)
                from_block = block_data.from_block
                to_block = block_data.to_block

                from_block_date = self.blockchain.get_block_date(from_block)
                to_block_date = self.blockchain.get_block_date(to_block)

                print(f"Block Range {from_block}-{to_block} ({from_block_date} to {to_block_date})")
                print(f"For timestamp: {datetime.fromtimestamp(timestamp)} + {duration} days")
                print(f"{abs(from_block - to_block)} total blocks")
                print(" > -----")

                print(" > Get batch of transactions for each day there was a significant appreciation in price")
                for pool_contract in pool_contracts:

                    print(f"Recursively splitting blocks in chunks of 10k for {pool_contract} This could take a while")
                    transactions = Updater.get_transactions(
                        from_block=from_block, to_block=to_block,
                        contract=pool_contract, blockchain=self.blockchain
                    )

                    print(f"Found {len(transactions)} transactions")









