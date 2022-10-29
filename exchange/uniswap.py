import time

from blockchain_explorer.blockchain_explorer import Explorer
from uniswap import Uniswap
from wallets.models import PoolContract


class UniswapAPI(Explorer):
    def __init__(self, chain: str, address: str = None, private_key: str = None, version: int = 3, use_testnet: bool = False):
        """
        Uniswap API interface. Child of Web3.py class for node operations

        :param chain: Token chain
        :param address: EOA address
        :param private_key: private key string of EOA
        :param version: version
        :param use_testnet: testnet or mainnet
        """
        super(UniswapAPI, self).__init__(chain=chain, use_testnet=use_testnet)

        # checksum address is needed for web API
        self.MAIN_WALLET = address
        self.PRIVATE_KEY = private_key
        self.w3 = self.web3
        self.version = version

        # self.uni = Uniswap(address=address, private_key=private_key, version=version, provider=self.provider_url)
        self.POOL = PoolContract.objects.filter(version=self.version).get(name="uniswap")
        self.ROUTER_ADDRESS = self.POOL.address
        self.ROUTER_ABI = self.POOL.abi
        self.WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    def get_router_contract(self):
        """
        :return: Contract object
        """
        return self.web3.eth.contract(address=self.ROUTER_ADDRESS, abi=self.ROUTER_ABI)

    def swap_token_for_eth(self, token_address: str, amount_out, max_gas: int = 200000):
        """
        swap token for ETH
        :param token_address: address of token to swap
        :param amount_out: Amount to swap
        :param max_gas: MAX gas to use
        :return:
        """

        nonce = self.web3.eth.getTransactionCount(self.MAIN_WALLET)
        contract = self.get_router_contract()

        swap_transaction = contract.functions.swapExactTokensForTokens(
            0,
            [self.WETH, token_address],
            self.MAIN_WALLET,  # Main address function is called from, and receiver address
            int(time.time()) + (60*20),  # 20 min timeout
        ).buildTransaction({
            "nonce": nonce,
            "gas": max_gas,
            "gasPrice": self.web3.eth.gasPrice,
            "from": self.MAIN_WALLET,
            "value": self.web3.toWei("0.01", "ether")
        })

        signed_tx = self.web3.eth.signTransaction(swap_transaction, self.PRIVATE_KEY)
        send_tx = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        transaction_hash = self.web3.toHex(send_tx)
        return transaction_hash

















