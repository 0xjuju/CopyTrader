from datetime import datetime
from typing import Any

from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan


class Wallet:
    def __init__(self, address: str, chain: str):
        self.blockchain = Blockchain(chain)
        self.blockscan = Blockscan(chain)
        self.address = self.blockchain.checksum_address(address)

    def _average_time_between_blocks_for_swap_events(self, swap_events: list[dict[str, Any]]):
        dates = [datetime.fromtimestamp(int(i["timeStamp"])) for i in swap_events]
        time_diffs = list()

        for index, d in enumerate(dates):
            try:
                diff = abs(d - dates[index + 1])
                print(diff)
                time_diffs.append(diff.total_seconds())  # Total difference in seconds of d and the next value
            except IndexError:  # End of list is reached
                pass
        average = sum(time_diffs) / len(dates)

        return average





    def get_swap_events_for_wallet(self, max_events: int = 100) -> list[dict[str, Any]]:
        normal_tx_list = self.blockscan.get_normal_transaction_list(address=self.address)

        try:
            tx_list = normal_tx_list["result"][-max_events:]
        except IndexError:  # total transaction list is less than max_events

            tx_list = normal_tx_list["result"]

        return [i for i in tx_list if "swap" in i["functionName"] or "execute" in i["functionName"]]

    def is_likely_bot(self) -> bool:
        pass





