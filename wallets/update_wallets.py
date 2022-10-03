from collections import defaultdict
from datetime import datetime, timedelta
import json
import time

import web3

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain_explorer.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from etherscan.etherscan_api import Etherscan
from wallets.models import Bot, Transaction, Wallet, PoolContract


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
        for index, datapoint in enumerate(price_breakouts):
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
            transactions = blockchain.filter_contract(contract_address=token.uniswap_contract, from_block=from_block,
                                                      to_block=to_block)

            # Exclude known bot wallets from processing
            blacklisted = Bot.objects.values_list("address", flat=True)

            buyers = defaultdict(list)
            sellers = defaultdict(list)

            whitelisted_contracts = PoolContract.objects.values_list("address", flat=True)
            all_entries = transactions.get_all_entries()
            print(f"Number of transactions: {len(all_entries)}")

            for transaction in all_entries:

                checked_topics = [blockchain.convert_to_checksum_address(i) for i in transaction["topics"]]

                if checked_topics[1] in whitelisted_contracts and checked_topics[2] not in whitelisted_contracts and\
                        blockchain.web3.eth.get_code(checked_topics[2]) == b'':

                    to_address = checked_topics[1]

                    if to_address not in blacklisted and to_address[0:12] != "0x0000000000":
                        from_address = checked_topics[2]

                        data = transaction["data"]
                        topics = [i.hex() for i in transaction["topics"]]

                        decoded_log = blockchain.decode_log(data=data, topics=topics, abi=token.uniswap_abi)

                        if decoded_log[0] == "Swap":
                            log_data = json.loads(decoded_log[1])

                            amount0 = log_data["amount0"]
                            amount1 = log_data["amount1"]

                            # amount0 as negative number represents main asset as sold

                            if amount0 > 0:
                                sellers[from_address].append((1, transaction, amount1))

                            elif amount0 < 0:
                                buyers[from_address].append((1, transaction, amount0))

            #
            filtered_transactions = list()
            for buyer, values in buyers.items():
                if sellers.get(buyer) is None:
                    for value in values:
                        filtered_transactions.append((buyer, value[1], value[2]))
                else:
                    for value in values:
                        if value[0] < 5:
                            filtered_transactions.append((buyer, value[1], value[2]))

            for transaction_data in filtered_transactions:
                address = transaction_data[0]
                transaction = transaction_data[1]
                amount = transaction_data[2] / (10 ** 18)

                wallet, created = Wallet.objects.get_or_create(address=address)
                if created:
                    wallet.save()
                wallet.token.add(token)
                transaction_hash = transaction["transactionHash"].hex()

                if not Transaction.objects.filter(transaction_hash=transaction_hash).exists():
                    transaction = Transaction.objects.create(
                        transaction_hash=transaction_hash,
                        token_in=token.name,
                        wallet=wallet,
                        amount=amount,
                        percent=percentage,
                        timestamp=datetime.fromtimestamp(timestamp)
                    )

                    transaction.save()
            print(f"Done batch {index+1}: {datetime.fromtimestamp(timestamp)}")
        print("Finished")

















