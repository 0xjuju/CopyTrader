from collections import defaultdict
from datetime import datetime, timedelta
import json
import time

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain_explorer.blockchain_explorer import Explorer
from blockchain_explorer.blockscsan import Blockscan
from coingecko.coingecko_api import GeckoClient
from wallets.models import Bot, Transaction, Wallet, PoolContract


class Updater:

    @staticmethod
    def create_database_entry(filtered_transactions, token, percentage, timestamp, index):
        """
        :param filtered_transactions:
        :param token:
        :param percentage:
        :param timestamp:
        :param index:
        :return:
        """
        all_transactions = Transaction.objects.all()
        for transaction_data in filtered_transactions:
            address = transaction_data[0]
            transaction = transaction_data[1]
            amount = transaction_data[2] / (10 ** 18)

            wallet, created = Wallet.objects.get_or_create(address=address)
            if created:
                wallet.save()
            wallet.token.add(token)
            transaction_hash = transaction["transactionHash"].hex()

            if not all_transactions.filter(transaction_hash=transaction_hash).exists():
                transaction = Transaction.objects.create(
                    transaction_hash=transaction_hash,
                    token_in=token.name,
                    wallet=wallet,
                    amount=amount,
                    percent=percentage,
                    timestamp=datetime.fromtimestamp(timestamp)
                )

                transaction.save()
        print(f"Done batch {index + 1}: {datetime.fromtimestamp(timestamp)}")


    @staticmethod
    def create_date_range(duration, timestamp, explorer):
        # create from_block and to_block range relative to price breakout timeframe
        if duration == 1:
            before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=5)
            three_days_into_breakout_timestamp = before_breakout_timestamp
        else:
            before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=7 - duration)
            three_days_into_breakout_timestamp = before_breakout_timestamp + timedelta(days=4)

            # if three_days_into_breakout_timestamp - before_breakout_timestamp > 5
        try:
            from_block = int(explorer.get_block_by_timestamp(int(before_breakout_timestamp.timestamp()))["result"])
            to_block = int(
                explorer.get_block_by_timestamp(int(three_days_into_breakout_timestamp.timestamp()))["result"])
        except ValueError as e:
            print(e)
            time.sleep(5)
            from_block = int(explorer.get_block_by_timestamp(int(before_breakout_timestamp.timestamp()))["result"])
            to_block = int(
                explorer.get_block_by_timestamp(int(three_days_into_breakout_timestamp.timestamp()))["result"])

        return from_block, to_block

    @staticmethod
    def determine_price_breakouts(diffs, timestamps):
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

        return price_breakouts

    @staticmethod
    def get_prices_data(contract_address, chain):
        # Get last 100 days of prices for token
        price_data = GeckoClient().get_market_chart_by_contract(contract_address=contract_address, chain=chain)
        price_data = price_data["prices"]
        timestamps = [i[0] for i in price_data]
        prices = [i[1] for i in price_data]

        return timestamps, prices

    @staticmethod
    def contract_and_address_validated(checked_topics, whitelisted_contracts, blacklisted, blockchain):
        to_address = checked_topics[1]
        if checked_topics[1] in whitelisted_contracts and checked_topics[2]\
                not in whitelisted_contracts and blockchain.web3.eth.get_code(checked_topics[2]) == b'' \
                and to_address not in blacklisted and to_address[0:12] != "0x0000000000":
            return True

    def map_buyers_and_sellers(self, blockchain, all_entries, blacklisted, whitelisted, abi):
        buyers = defaultdict(list)
        sellers = defaultdict(list)

        for transaction in all_entries:
            # We want at least 2 topics to filter out Sync event, and other non-swap events
            if len(transaction["topics"]) > 2:
                checked_topics = [blockchain.convert_to_checksum_address(i) for i in transaction["topics"]]

                # Various checks to filter out contracts that execute buy/sell events
                # Expect real person to always interact directly with DEX
                if self.contract_and_address_validated(checked_topics=checked_topics, blacklisted=blacklisted,
                                                       whitelisted_contracts=whitelisted,
                                                       blockchain=blockchain):

                    # main wallet or EOA (Externally Operated Account)
                    from_address = checked_topics[2]

                    data = transaction["data"]
                    topics = [i.hex() for i in transaction["topics"]]

                    decoded_log = blockchain.decode_log(data=data, topics=topics, abi=abi)

                    if decoded_log[0] == "Swap":
                        log_data = json.loads(decoded_log[1])

                        try:
                            # Uniswap V3 log data has different vs v2
                            amount0 = log_data["amount0"]
                            amount1 = log_data["amount1"]
                            # amount0 as negative number represents main asset as sold

                            if amount0 > 0:
                                sellers[from_address].append((1, transaction, amount1))

                            elif amount0 < 0:
                                buyers[from_address].append((1, transaction, amount0))

                        except KeyError:
                            # Try for V3 first. If Key Error, try V2 syntax
                            if from_address == log_data["to"] and log_data["amount0Out"] > 0:
                                buyers[from_address].append((1, transaction, log_data["amount0Out"]))

                            elif from_address == log_data["to"] and log_data["amount1Out"] > 0:
                                sellers[from_address].append((1, transaction, log_data["amount0In"]))

                            # We want to classify as either BUYER or SELLER always using these criteria
                            else:
                                raise Exception(f"Unidentified error\n {transaction['transactionHash'].hex(), log_data}")

        return buyers, sellers

    def update(self, token):
        # Blockchain service explorer
        explorer = Blockscan(token.chain)

        # web3.py
        blockchain = Explorer(token.chain)

        timestamps, prices = self.get_prices_data(token.address, chain=token.chain)

        # Percentage difference of each price relative to the next day, 3 days, and 7 days from price
        diffs = percent_difference_from_dataset(prices)

        # determine if a price increase that meets threshold is reached and add to list
        price_breakouts = self.determine_price_breakouts(diffs=diffs, timestamps=timestamps)

        if price_breakouts:
            # Exclude known bot wallets from processing
            blacklisted = Bot.objects.values_list("address", flat=True)

            # Contracts that interact with humans
            whitelisted = PoolContract.objects.values_list("address", flat=True)

            for index, datapoint in enumerate(price_breakouts):
                duration = datapoint[0]
                timestamp = datapoint[1]
                percentage = datapoint[2]

                # Check if format has changed for any timestamp. Expect the last 5 digits to always be zero. Date only
                if str(timestamp)[-5:] != "00000":
                    raise Exception("Will not format correctly")
                timestamp = int(timestamp / 1000)

                # Convert datetime to range of blocks to look through
                from_block, to_block = self.create_date_range(duration=duration, timestamp=timestamp, explorer=explorer)

                transactions = blockchain.filter_contract(contract_address=token.uniswap_contract, from_block=from_block,
                                                          to_block=to_block)

                print(f"Number of transactions: {len(transactions)}")

                # Separate Buyers from Sellers for each transaction and create Dictionary representations
                # Wallet address (EOA) as KEY
                buyers, sellers = self.map_buyers_and_sellers(blockchain=blockchain, all_entries=transactions,
                                                              blacklisted=blacklisted, whitelisted=whitelisted,
                                                              abi=token.uniswap_abi)

                # Loop through buyers and sellers to create list of transaction excluding ones likely done by bots
                filtered_transactions = list()
                for buyer, values in buyers.items():

                    # Whitelist address since FrontRunner bots should always have sales transactions
                    # Assumes token with high enough volume that buy and sale happens within this range of blocks
                    # possible to miss bots within transactions on front or end of block
                    if sellers.get(buyer) is None:
                        for value in values:
                            filtered_transactions.append((buyer, value[1], value[2]))
                    else:
                        for value in values:
                            # Assumption that most real buyer will not have more than 5 buy events in a single block
                            if value[0] < 5:
                                filtered_transactions.append((buyer, value[1], value[2]))

                # Update Database with new wallets and transactions
                self.create_database_entry(filtered_transactions=filtered_transactions, token=token,
                                           timestamp=timestamp, percentage=percentage, index=index)
            print("Finished")

















