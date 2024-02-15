from datetime import datetime
from typing import Any

from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan


class Seconds:
    def __init__(self, seconds: float):
        self.seconds = seconds

    def minutes(self):
        return self.seconds / 60

    def hours(self):
        return self.minutes() / 60

    def days(self):
        return self.hours() / 24

    def weeks(self):
        return self.days() / 7


class Wallet:
    def __init__(self, address: str, chain: str):
        self.blockchain = Blockchain(chain)
        self.blockscan = Blockscan(chain)
        self.address = self.blockchain.checksum_address(address)

    @staticmethod
    def _average_time_between_transactions(events: list[dict[str, Any]]) -> Seconds:
        dates = [datetime.fromtimestamp(int(i["timeStamp"])) for i in events]
        time_diffs = list()

        for index, d in enumerate(dates):
            try:
                diff = abs(d - dates[index + 1])
                time_diffs.append(diff.total_seconds())  # Total difference in seconds of d and the next value
            except IndexError:  # End of list is reached
                pass
        average = sum(time_diffs) / len(dates)

        return Seconds(average)

    def get_transactions_for_wallet(self, max_events: int = 100) -> list[dict[str, Any]]:
        normal_tx_list = self.blockscan.get_normal_transaction_list(address=self.address)

        try:
            tx_list = normal_tx_list["result"][-max_events:]
        except IndexError:  # total transaction list is less than max_events

            tx_list = normal_tx_list["result"]

        return tx_list

    def is_likely_bot(self) -> bool:
        pass





