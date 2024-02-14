import blockchain.decorators
from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan


class Wallet:
    def __init__(self, address: str, chain: str):
        self.blockchain = Blockchain(chain)
        self.blockscan = Blockscan(chain)
        self.address = self.blockchain.checksum_address(address)

    def is_likely_bot(self,) -> bool:

        normal_tx_list = self.blockscan.get_normal_transaction_list(address=self.address)
        txs = normal_tx_list["result"]

        for tx in txs:
            if "swap" in tx["functionName"]:
                print(tx)





