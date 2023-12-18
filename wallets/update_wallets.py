from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import time

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain.blockchain_explorer import Explorer
from blockchain.blockscsan import Blockscan
from coingecko.coingecko_api import GeckoClient
from coingecko.models import GeckoToken
from wallets.models import Bot, Transaction, Wallet, PoolContract, Token, PairContract


class Updater:

    @staticmethod
    def contract_and_address_validated(checked_topics, whitelisted_contracts, blacklisted, blockchain):
        """
        Validate address against known automated addresses

        :param checked_topics: transaction data containing various contract interactions
        :param whitelisted_contracts: Accepted addresses interacted..
        :param blacklisted: Known automated addresses
        :param blockchain: chain
        :return: Boolean whitelisted or not
        """

        to_address = checked_topics[1]
        if checked_topics[1] in whitelisted_contracts and checked_topics[2] \
                not in whitelisted_contracts and blockchain.web3.eth.get_code(checked_topics[2]) == b'' \
                and to_address not in blacklisted and to_address[0:12] != "0x0000000000":
            return True

    @staticmethod
    def create_database_entry(filtered_transactions: list[tuple[str, dict, float]], token: Token, chain: str, percentage: str,
                              timestamp: int, index: int) -> None:
        """
        :param filtered_transactions: transaction data with possible bots / unwanted accounts filtered out
        :param token: Token model
        :param chain: chain
        :param percentage: percentage increase from price breakout
        :param timestamp: Timestamp before breakout
        :param index: Index for batch
        """

        # Previous transactions fom database. Used to check against duplciate entries
        all_transactions = Transaction.objects.all()

        for transaction_data in filtered_transactions:
            address = transaction_data[0]

            # raw tx data
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
    def create_block_range(duration: int, timestamp: int, explorer: Blockscan) -> (int, int):
        """
        :param duration: number of days it took for price to break out relative to start date
        :param timestamp: start date of breakout
        :param explorer: blockchain explorer service e.g. etherscan...
        :return: block range
        """
        # create from_block and to_block range relative to price breakout timeframe
        if duration == 1:
            before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=5)
            three_days_into_breakout_timestamp = before_breakout_timestamp
        else:
            before_breakout_timestamp = datetime.fromtimestamp(timestamp) - timedelta(days=7 - duration)
            three_days_into_breakout_timestamp = before_breakout_timestamp + timedelta(days=4)

        # price outbreak is recent, day later will be in the future
        if three_days_into_breakout_timestamp > datetime.now():
            three_days_into_breakout_timestamp = datetime.now() - timedelta(minutes=10)

            # if three_days_into_breakout_timestamp - before_breakout_timestamp > 5
        try:
            from_block = explorer.get_block_by_timestamp(int(before_breakout_timestamp.timestamp()))
            to_block = explorer.get_block_by_timestamp(int(three_days_into_breakout_timestamp.timestamp()),
                                                       look_for_previous_block_if_error=True)
        except ValueError as e:
            print(e)
            time.sleep(5)
            from_block = explorer.get_block_by_timestamp(int(before_breakout_timestamp.timestamp()))
            to_block = explorer.get_block_by_timestamp(int(three_days_into_breakout_timestamp.timestamp()),
                                                       look_for_previous_block_if_error=True)

        # If block is not found, error message returned. Catch Value error when converting to integer
        try:
            return int(from_block), int(to_block)
        except ValueError as e:
            print(e)
            return None, None

    @staticmethod
    def determine_price_breakouts(diffs: list[tuple], timestamps: list[int], percent_threshold: float)\
            -> list[tuple[int, int, float]]:
        """
        :param diffs: percentage difference of price tracked from its start date to day 1, 3, and 7
        :param timestamps: list of timestamps for each diff
        :param percent_threshold: minimum price increase percentage
        :return: Number of days to look before breakout date, its correlating starting timestamp, and percent increase
        """
        price_breakouts = list()
        # Find timeframes where prices increased by at least 20% and store start date and percentage in list
        for index, d in enumerate(diffs):

            # determine number of days before first price increase
            start_date = None
            if d[0] > percent_threshold:
                start_date = 1
            elif d[1] > percent_threshold:
                start_date = 3
            elif d[2] > percent_threshold:
                start_date = 7

            # only append data if a start date of price increase is found
            if start_date:

                # largest move percentage within the three timeframes. Used to avoid duplicate data
                largest_price_move = (max(d) - 1) * 100
                price_breakouts.append(
                    (start_date, timestamps[index], largest_price_move)
                )

        return price_breakouts

    @staticmethod
    def filter_transactions(buyers: dict[str, list], sellers: dict[str, list]):
        """
        :param buyers: ...
        :param sellers: ...
        :return:
        """
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
                    # Assumption that most real buyers will not have more than 5 buy events in a single block
                    if value[0] == 1:
                        filtered_transactions.append((buyer, value[1], value[2]))

        # Number of tx for each account
        tx_count = Counter(i[0] for i in filtered_transactions)
        # further filter tx for accounts with less than 4
        filtered_transactions = [i for i in filtered_transactions if tx_count[i[0]] == 1]
        return filtered_transactions

    @staticmethod
    def get_prices_data(contract_address: str, chain: str) -> tuple[list, list]:
        """
        :param contract_address: contract address of token
        :param chain: token chain
        :return: list of timestamps and related prices
        """

        # Get last 100 days of prices for token
        price_data = GeckoClient().get_market_chart_by_contract(contract_address=contract_address, chain=chain)
        price_data = price_data["prices"]
        timestamps = [i[0] for i in price_data]
        prices = [i[1] for i in price_data]

        return timestamps, prices

    @staticmethod
    def get_transactions(from_block: int, to_block: int, contract: PairContract, blockchain: Explorer):
        """
        :param from_block: start of block range
        :param to_block: end of block range
        :param contract: Pair Contract of token from dex
        :param blockchain: blockchain explorer
        :return: List of transactions filtered by token-pair contract from various dex
        """

        # Block range for query
        max_chunk = None
        if contract.chain == "binance-smart-chain":
            max_chunk = 500

        # Infura HTTPS for Polygon does not support eth.get_newFilter so get_logs is used instead
        if contract.chain == "polygon" or contract.chain == "polygon-pos":
            max_chunk = 3500

            transactions = blockchain.get_logs(max_chunk=max_chunk, address=contract.contract_address,
                                               fromBlock=from_block, toBlock=to_block)
        else:
            transactions = blockchain.filter_contract(max_chunk=max_chunk, address=contract.contract_address,
                                                      fromBlock=from_block, toBlock=to_block)

        return transactions

    def map_buyers_and_sellers(self, blockchain, all_entries, blacklisted, whitelisted, abi):
        """
        :param blockchain: chain
        :param all_entries: list of transaction from given timeframe
        :param blacklisted: Known automated addressses
        :param whitelisted: valid addresses
        :param abi: Application Binary Interface
        :return: Parsed list of buyers vs sellers
        """
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

    def update(self, percent_threshold: float):

        print(contracts)

        for contract in contracts:
            # Blockchain (etherscan, bscscan) service explorer
            explorer = Blockscan(contract.chain)

            # web3.py
            blockchain = Explorer(contract.chain)

            timestamps, prices = self.get_prices_data(token.address, chain=contract.chain)

            # Percentage difference of each price relative to the next day, 3 days, and 7 days from price
            diffs = percent_difference_from_dataset(prices)

            # determine if a price increase that meets threshold is reached and add to list
            price_breakouts = self.determine_price_breakouts(diffs=diffs, timestamps=timestamps,
                                                             percent_threshold=percent_threshold)
            if price_breakouts:
                # Exclude known bot wallets from processing
                blacklisted = Bot.objects.values_list("address", flat=True)

                # Contracts that interact with humans
                whitelisted = PoolContract.objects.values_list("address", flat=True)

                for index, datapoint in enumerate(price_breakouts):
                    duration = datapoint[0]
                    timestamp = datapoint[1]
                    percentage = datapoint[2]

                    # Check if format has changed for any timestamp. Expect last 5 digits to always be zero. Date only
                    if str(timestamp)[-5:] != "00000":
                        raise Exception("Will not format correctly")
                    timestamp = int(timestamp / 1000)

                    # Convert datetime to range of blocks to look through
                    from_block, to_block = self.create_block_range(duration=duration, timestamp=timestamp, explorer=explorer)
                    if from_block and to_block:

                        transactions = self.get_transactions(from_block=from_block, to_block=to_block, contract=contract,
                                                             blockchain=blockchain)

                        print(f"Number of transactions: {len(transactions)}")

                        # Separate Buy ers from Sellers for each transaction and create Dictionary representations
                        # Wallet address (EOA) as KEY
                        buyers, sellers = self.map_buyers_and_sellers(blockchain=blockchain, all_entries=transactions,
                                                                      blacklisted=blacklisted, whitelisted=whitelisted,
                                                                      abi=contract.abi)

                        # transactions with unwanted accounts filtered out
                        filtered_transactions = self.filter_transactions(buyers, sellers)

                        # Update Database with new wallets and transactions
                        self.create_database_entry(filtered_transactions=filtered_transactions, token=token,
                                                   chain=contract.chain, timestamp=timestamp, percentage=str(percentage)
                                                   ,index=index)
            print("Finished")

















