
from blockchain.alchemy import Blockchain
from blockchain.tests.build_test_data import build_factory_contracts
from django.test import TestCase


class TestAlchemy(TestCase):
    def setUp(self) -> None:
        self.eth_blockchain = Blockchain("ethereum")
        self.arbitrum_blockchain = Blockchain("arbitrum-one")
        self.polygon_blockchain = Blockchain("polygon-pos")
        self.factory_contracts = build_factory_contracts()

    def test_is_connected(self):
        self.assertTrue(self.eth_blockchain.is_connected(), True)
        self.assertTrue(self.arbitrum_blockchain.is_connected(), True)
        self.assertTrue(self.polygon_blockchain.is_connected(), True)

    def test_checksum_address(self):
        address = "0x8ee325ae3e54e83956ef2d5952d3c8bc1fa6ec27"
        checked_address = self.eth_blockchain.checksum_address(address)
        self.assertEqual(checked_address, "0x8EE325AE3E54e83956eF2d5952d3C8Bc1fa6ec27")

    def test_get_factory_pools(self):
        univ3 = self.factory_contracts["uniswapv3"]

        # Ethereum Pool
        contract = self.eth_blockchain._get_contract(univ3["contract"], abi=univ3["abi"])
        pools = self.eth_blockchain.get_factory_pools(
            contract, argument_filters={"token1": "0x8ee325ae3e54e83956ef2d5952d3c8bc1fa6ec27"})
        self.assertEqual(pools[0]["token1"], "0x8EE325AE3E54e83956eF2d5952d3C8Bc1fa6ec27")

        # Arbitrum Pool
        contract = self.arbitrum_blockchain._get_contract(univ3["contract"], abi=univ3["abi"])
        pools = self.arbitrum_blockchain.get_factory_pools(
            contract, argument_filters={"token1": "0xc8ccbd97b96834b976c995a67bf46e5754e2c48e"})
        self.assertEqual(pools[0]["token1"], "0xc8CCBd97b96834b976C995a67BF46e5754e2C48E")

        uniswapv3poly = self.factory_contracts["uniswapv3poly"]
        # Polygon Pool on Uniswap
        contract = self.polygon_blockchain._get_contract(uniswapv3poly["contract"], abi=uniswapv3poly["abi"])
        pools = self.polygon_blockchain.get_factory_pools(
            contract, argument_filters={"token0": "0xe5417af564e4bfda1c483642db72007871397896"})
        self.assertEqual(pools[0]["token0"], "0xE5417Af564e4bFDA1c483642db72007871397896")

        quickswapv3 = self.factory_contracts["quickswapv3"]
        # Polygon Pool on Quickswap
        contract = self.polygon_blockchain._get_contract(quickswapv3["contract"], abi=quickswapv3["abi"])
        pools = self.polygon_blockchain.get_factory_pools(
            contract, argument_filters={"token0": "0x229b1b6c23ff8953d663c4cbb519717e323a0a84"})
        self.assertEqual(pools[0]["token0"], "0x229b1b6C23ff8953D663C4cBB519717e323a0a84")

        camelotv3 = self.factory_contracts["camelotv3"]
        # Arbitrum Pool on Camelot dex v3
        contract = self.arbitrum_blockchain._get_contract(camelotv3["contract"], abi=camelotv3["abi"])
        pools = self.arbitrum_blockchain.get_factory_pools(
            contract, argument_filters={"token1": "0xf19547f9ed24aa66b03c3a552d181ae334fbb8db"})
        self.assertEqual(pools[0]["token1"], "0xF19547f9ED24aA66b03c3a552D181Ae334FBb8DB")

        camelotv2 = self.factory_contracts["camelotv2"]
        # Arbitrum Pool on Camelot dex v2
        contract = self.arbitrum_blockchain._get_contract(camelotv2["contract"], abi=camelotv2["abi"])
        pools = self.arbitrum_blockchain.get_factory_pools(
            contract, argument_filters={"token1": "0xf19547f9ed24aa66b03c3a552d181ae334fbb8db"})
        self.assertEqual(pools[0]["token1"], "0xF19547f9ED24aA66b03c3a552D181Ae334FBb8DB")

        sushiswapv3polygon = self.factory_contracts["sushiswapv3polygon"]
        # Polygon pool on Sushiwap v3
        contract = self.polygon_blockchain._get_contract(sushiswapv3polygon["contract"], abi=sushiswapv3polygon["abi"])
        pools = self.polygon_blockchain.get_factory_pools(
            contract, argument_filters={"token0": "0x071ac29d569a47ebffb9e57517f855cb577dcc4c"})
        self.assertEqual(pools[0]["token0"], "0x071AC29d569a47EbfFB9e57517F855Cb577DCc4C")

    def test_query_filter(self):
        from_block = 18967710
        to_block = from_block + 100
        filter_object = self.eth_blockchain.w3.eth.get_logs
        logs = self.eth_blockchain._query_filter(filter_object, fromBlock=from_block, toBlock=to_block)






