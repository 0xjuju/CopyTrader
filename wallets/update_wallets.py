from datetime import datetime, timedelta
from hexbytes import HexBytes
import json
import time

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain_explorer.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from etherscan.etherscan_api import Etherscan
from wallets.models import Bot, PoolContract, Transaction, Wallet


def updater(token):
    etherscan = Etherscan()
    blockchain = Explorer(token.chain)

    # Get last 100 days of prices for token
    price_data = GeckoClient().get_market_chart_by_contract(contract_address=token.address, chain=token.chain)
    price_data = price_data["prices"]
    timestamps = [i[0] for i in price_data]
    prices = [i[1] for i in price_data]

    # Percentage difference of each price relative to the next day, 3 days, and 7 days from price
    diffs = percent_difference_from_dataset(prices)

    price_breakouts = list()
    # Find timeframes where prices increased by at least 20% and store start date and percentage in list
    for index, d in enumerate(diffs):

        # determine number of days before first price increase
        start_date = None
        if d[0] > 1.20:
            start_date = 1
        elif d[1] > 1.20:
            start_date = 3
        elif d[2] > 1.20:
            start_date = 7

        # only append data if a start date of price increase is found
        if start_date:
            price_breakouts.append(
                (start_date, timestamps[index], (max(d) - 1) * 100)
            )

    if price_breakouts:
        for datapoint in price_breakouts:
            duration = datapoint[0]
            timestamp = datapoint[1]
            percentage = datapoint[2]

            # Check if formatting has changed for any timestamp. Expect the last 5 digits to always be zero. Date only
            if str(timestamp)[-5:] != "00000":
                raise Exception("Will not format correctly")

            timestamp = int(timestamp / 1000)

            # create from_block and to_block range relative to price breakout timeframe
            if duration == 1:
                before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=5)
                three_days_into_breakout_timestamp = before_breakout_timestamp
            else:
                before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=8 - duration)
                three_days_into_breakout_timestamp = before_breakout_timestamp + timedelta(days=4)

            from_block = int(etherscan.get_block_by_timestamp(int(before_breakout_timestamp.timestamp()))["result"])
            to_block = int(etherscan.get_block_by_timestamp(int(three_days_into_breakout_timestamp.timestamp()))["result"])
            # delay to bypass rate limit
            time.sleep(0.5)

            blacklisted = Bot.objects.values_list("address", flat=True)

            transactions = blockchain.filter_contract(contract_address=token.uniswap_contract, from_block=from_block,
                                                      to_block=to_block)

            for transaction in transactions.get_all_entries():
                to_address = blockchain.convert_to_checksum_address(transaction["topics"][1])

                if to_address not in blacklisted and to_address[0:12] != "0x0000000000":
                    from_address = blockchain.convert_to_checksum_address(transaction["topics"][2])

                    data = transaction["data"]
                    topics = [i.hex() for i in transaction["topics"]]
                    transaction_hash = transaction["transactionHash"].hex()

                    decoded_log = blockchain.decode_log(data=data, topics=topics, abi=token.uniswap_abi)

                    if decoded_log[0] == "Swap":
                        log_data = json.loads(decoded_log[1])

                        amount0 = log_data["amount0"]
                        if amount0 < 0:
                            amount0 = amount0 / (10 ** 18)
                            wallet, created = Wallet.objects.get_or_create(address=from_address)
                            if created:
                                wallet.save()
                            wallet.token.add(token)

                            transaction = Transaction.objects.create(
                                transaction_hash=transaction_hash,
                                token_in=token.name,
                                wallet=wallet,
                                amount=amount0,
                                percent=percentage,
                                timestamp=datetime.fromtimestamp(timestamp)
                            )
                            transaction.save()

















