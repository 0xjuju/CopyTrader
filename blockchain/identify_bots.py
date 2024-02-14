from typing import Any

from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan


class Wallet:
    def __init__(self, address: str, chain: str):
        self.blockchain = Blockchain(chain)
        self.blockscan = Blockscan(chain)
        self.address = self.blockchain.checksum_address(address)

    def _average_time_between_blocks_for_swap_events(self):
        pass

    def get_swap_events_for_wallet(self, max_events: int = 100) -> list[dict[str, Any]]:
        normal_tx_list = self.blockscan.get_normal_transaction_list(address=self.address)

        try:
            tx_list = normal_tx_list["result"][0:max_events]
        except IndexError:  # total transaction list is less than max_events

            tx_list = normal_tx_list["result"]
            tx_list = tx_list[0:len(tx_list)]

        return [i for i in tx_list if "swap" in i["functionName"]]

    def is_likely_bot(self) -> bool:
        pass





