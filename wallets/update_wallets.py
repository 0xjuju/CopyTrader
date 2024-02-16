from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import time
from typing import Union, Any

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan
from blockchain.models import Chain, ABI, FactoryContract
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address
from django.db.models import Q
from wallets.models import Bot, Transaction, Wallet, Token


class CoingeckoPriceBreakout:
    day: int
    timestamp: int
    largest_price_move: float

    def __init__(self, day: int, timestamp: int, largest_price_move: float):
        """
        :param day: number of days to look before the start of a price breakout
        :param timestamp: start date of price breakout
        :param largest_price_move: Largest percent price move of token after price breakout
        """
        self.day = day
        self.timestamp = timestamp
        self.largest_price_move = largest_price_move


class Swap:
    transaction: dict[str, Any]
    side: str
    count: int
    amount: int

    def __init__(self, transaction: dict[str, Any], side: str, amount: int, count: int = 1):
        """

        :param transaction: Transaction data of swap
        :param side: buy or sell event
        :param amount: amount bought or sold
        :param count: number of swaps
        """
        self.transaction = transaction
        self.side = side
        self.amount = amount
        self.count = count

        sides = ["buy", "sell"]
        if side not in sides:
            raise ValueError(f"{side} not a valid options. Choices are {sides}")

class Updater:

    @staticmethod
    def contract_and_address_validated(checked_topics: list[str], blacklisted: list[str], blockchain: Blockchain):
        """
        Validate address against known automated addresses

        :param checked_topics: transaction data containing various contract interactions
        :param blacklisted: Known automated addresses
        :param blockchain: chain
        :return: Boolean whitelisted or not
        """

        to_address = checked_topics[1]

        if blockchain.w3.eth.get_code(checked_topics[2]) == b'' and to_address not in blacklisted:

            return True

    @staticmethod
    def create_database_entry(filtered_transactions: list[tuple[str, dict, float]], token: Token, chain: str,
                              percentage: str, timestamp: int, index: int) -> None:
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

            if wallet.token.filter(address=token.address).exists() is False:
                wallet.token.add(token)

            transaction_hash = transaction["transactionHash"].hex()
            if not all_transactions.filter(transaction_hash=transaction_hash).exists():

                try:
                    transaction = Transaction.objects.create(
                        transaction_hash=transaction_hash,
                        chain=chain,
                        token_in=token.name,
                        wallet=wallet,
                        amount=amount,
                        percent=percentage,
                        timestamp=datetime.fromtimestamp(timestamp)
                    )
                except Exception as e:
                    print(timestamp)
                    raise OSError(e, timestamp)

                transaction.save()
        print(f"Done batch {index + 1}: {datetime.fromtimestamp(timestamp)}")

    @staticmethod
    def create_block_range(duration: int, timestamp: int, explorer: Blockscan) -> (int, int):

        """
        :param duration: number of days it took for price to break out relative to start date
        :param timestamp: start-date of breakout
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

        days_ago_116 = datetime.now() - timedelta(days=116)
        print(before_breakout_timestamp, three_days_into_breakout_timestamp)
        if before_breakout_timestamp < days_ago_116 or three_days_into_breakout_timestamp < days_ago_116:
            raise ValueError(f" timstamps should never be less than 116 days before now {before_breakout_timestamp},"
                             f" {three_days_into_breakout_timestamp}")

        # If block is not found, error message returned. Catch Value error when converting to integer
        return int(from_block), int(to_block)

    @staticmethod
    def determine_price_breakouts(diffs: list[tuple], timestamps: list[int], percent_threshold: float)\
            -> list[CoingeckoPriceBreakout]:
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
            if (d[0] - 1) * 100 > percent_threshold:
                start_date = 1
            elif (d[1] - 1) * 100 > percent_threshold:
                start_date = 3
            elif (d[2] - 1) * 100 > percent_threshold:
                start_date = 7

            # only append data if a start date of price increase is found
            if start_date:

                # largest move percentage within the three timeframes. Used to avoid duplicate data
                largest_price_move = (max(d) - 1) * 100
                price_breakouts.append(
                    CoingeckoPriceBreakout(day=start_date, timestamp=timestamps[index], largest_price_move=largest_price_move)
                )

        return price_breakouts

    @staticmethod
    def filter_transactions(buyers: dict[str, list[Swap]], sellers: dict[str, list[Swap]]):
        """
        :param buyers: ...
        :param sellers: ...
        :return:
        """
        # Loop through buyers and sellers to create list of transaction excluding ones likely done by bots
        filtered_transactions = list()
        for buyer, swaps in buyers.items():

            # Whitelist address since FrontRunner bots should always have sales transactions
            # Assumes token with high enough volume that buy and sale happens within this range of blocks
            # possible to miss bots within transactions on front or end of block
            if sellers.get(buyer) is None:
                for swap in swaps:
                    filtered_transactions.append((buyer, swap.transaction, swap.amount))
            else:
                for swap in swaps:
                    # Assumption that most real buyers will not have more than 5 buy events in a single block
                    if swap.count == 1:
                        filtered_transactions.append((buyer, swap.transaction, swap.amount))

        # Number of tx for each account
        tx_count = Counter(i[0] for i in filtered_transactions)
        # further filter tx for accounts 1 tx
        filtered_transactions = [i for i in filtered_transactions if tx_count[i[0]] == 1]
        return filtered_transactions

    @staticmethod
    def get_dex_pairs(blockchain: Blockchain, token_address: str) -> dict[str, dict[list[str, dict]]]:
        """
        Parse through pools created on dexes of chain and get token / pool addresses
        :param blockchain: Blockchain explorer
        :param token_address: Token Contract address
        :return: pool info
        """
        pools = {
            blockchain.chain: dict()
        }

        # Dex factory contracts
        factory_contracts = FactoryContract.objects.filter(chain=blockchain.chain)

        for factory in factory_contracts:
            print(factory.name)
            contract = blockchain.get_contract(factory.address, factory.abi)

            pools[factory.chain][factory.name] = {
                "pools": list(),
                "abi": factory.abi
            }

            get_pools = blockchain.get_factory_pools(contract, argument_filters={"token1": token_address})
            if not get_pools:
                get_pools = blockchain.get_factory_pools(contract, argument_filters={"token0": token_address})

            for pool in get_pools:
                pools[factory.chain][factory.name]["pools"].append(pool)

        return pools

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
    def get_transactions(from_block: int, to_block: int, contract: str, blockchain: Blockchain):
        """
        :param from_block: start of block range
        :param to_block: end of block range
        :param contract: Pair Contract of token from dex
        :param blockchain: blockchain explorer
        :return: List of transactions filtered by token-pair contract from various dex
        """
        print(f"Number of blocks: {abs(from_block - to_block):,}")
        print(from_block, "----", to_block)
        address = blockchain.checksum_address(contract)

        # Block range for query
        max_chunk = None
        if blockchain.chain == "binance-smart-chain":
            max_chunk = 500

        # Infura HTTPS for Polygon does not support eth.get_newFilter so get_logs is used instead
        if blockchain.chain == "polygon-pos":
            max_chunk = 3500

        transactions = blockchain.get_logs(max_chunk=max_chunk, address=address,
                                           fromBlock=from_block, toBlock=to_block)
        return transactions

    def map_buyers_and_sellers(self, blockchain: Blockchain, all_entries, blacklisted, abi: str) -> (
            defaultdict[list[Swap]],
            defaultdict[list[Swap]],
            ):
        """
        :param blockchain: chain
        :param all_entries: list of transaction from given timeframe
        :param blacklisted: Known automated addresses
        :param abi: Factory contract abi
        :return: List of Swap events for buyers and sellers
        """
        buyers = defaultdict(list)
        sellers = defaultdict(list)

        for transaction in all_entries:

            # We want at least 2 topics to filter out Sync event, and other non-swap events
            if len(transaction["topics"]) > 2:
                checked_topics = [transaction["topics"][0].hex()] +\
                                 [blockchain.convert_to_checksum_address_from_hex(i) for i in transaction["topics"][1:]]

                # Various checks to filter out contracts that execute buy/sell events
                # Expect real person to always interact directly with DEX
                if self.contract_and_address_validated(checked_topics=checked_topics, blacklisted=blacklisted,
                                                       blockchain=blockchain):

                    # main wallet or EOA (Externally Operated Account)
                    from_address = checked_topics[2]

                    data = transaction["data"]
                    topics = [i for i in transaction["topics"]]
                    decoded_log = blockchain.decode_log(data=data, topics=topics, abi=abi)
                    print(decoded_log)
                    print(transaction["transactionHash"].hex())

                    if decoded_log[0] == "Swap":
                        log_data = json.loads(decoded_log[1])

                        try:
                            # Uniswap V3 log data has different vs v2
                            amount0 = log_data["amount0"]
                            amount1 = log_data["amount1"]
                            # amount0 as negative number represents main asset as sold

                            if amount0 > 0:
                                sellers[from_address].append(Swap(transaction, "sell", amount1))

                            elif amount0 < 0:
                                buyers[from_address].append(Swap(transaction, "buy", amount0))

                        except KeyError:
                            # Try for V3 first. If Key Error, try V2 syntax
                            if from_address == log_data["to"] and log_data["amount0Out"] > 0:
                                buyers[from_address].append(Swap(transaction, "buy", log_data["amount0Out"]))

                            elif from_address == log_data["to"] and log_data["amount1Out"] > 0:
                                sellers[from_address].append(Swap(transaction, "sell", log_data["amount0In"]))

                            # We want to classify as either BUYER or SELLER always using these criteria
                            else:
                                raise Exception(f"Unidentified error\n {transaction['transactionHash'].hex(), log_data}")
        return buyers, sellers

    def update(self, percent_threshold: float):
        chains = Chain.objects.values_list("name", flat=True)

        v2pool_abi = ABI.objects.get(abi_type="v2pools").text
        v3pool_abi = ABI.objects.get(abi_type="v3pools").text

        # Pair contract and token addresses from Dex
        pools = dict()

        exclude_list = ["avalanche", "binance-smart-chain", "solana", "base", "optimistic-ethereum"]

        contracts = Address.objects.filter(chain__in=chains)\
            .exclude(chain__in=exclude_list)\
            .filter(processed=False)\
            .filter(
            token__price_change_24hr__gte=percent_threshold
        )
        print("Number of Contracts ", len(contracts))

        for contract in contracts:

            print(contract.token.name,  contract.chain)

            # Blockchain (etherscan, etc...) service explorer
            explorer = Blockscan(contract.chain)

            # web3.py
            blockchain = Blockchain(contract.chain)

            token_address = blockchain.checksum_address(contract.contract)

            # Get pool addresses for dexes on chain
            if pools.get(contract.chain) is None:
                pools.update(self.get_dex_pairs(blockchain, token_address))

            timestamps, prices = self.get_prices_data(contract.contract, chain=contract.chain)

            # Percentage difference of each price relative to the next day, 3 days, and 7 days from price
            diffs = percent_difference_from_dataset(prices)

            # determine if a price increase that meets threshold is reached and add to list
            price_breakouts = self.determine_price_breakouts(diffs=diffs, timestamps=timestamps,
                                                             percent_threshold=percent_threshold)

            if price_breakouts:
                # Exclude known bot wallets from processing
                blacklisted = Bot.objects.values_list("address", flat=True)

                for index, coingecko_breakout in enumerate(price_breakouts):
                    duration = coingecko_breakout.day
                    timestamp = coingecko_breakout.timestamp
                    percentage = coingecko_breakout.largest_price_move

                    # Check if format has changed for any timestamp. Expect last 5 digits to always be zero. Date only
                    if str(timestamp)[-5:] != "00000":
                        raise Exception(f"Will not format correctly. Debug {timestamp}")

                    # convert timestamp in milliseconds to seconds
                    timestamp = timestamp / 1000

                    # Convert datetime to range of blocks to look through
                    from_block, to_block = self.create_block_range(duration=duration, timestamp=timestamp,
                                                                   explorer=explorer)
                    if from_block and to_block:

                        try:
                            # Check dex and see if there's a match for the token pool, and extract the pool address
                            dex_list = pools[contract.chain]
                        except KeyError as e:
                            print(contract.token.name, print(contract.chain))
                            raise KeyError(e)

                        for dex, data in dex_list.items():
                            print(dex)
                            pool_contracts = list()
                            # factory_abi = data["abi"]
                            for pool_info in data["pools"]:
                                if pool_info["token0"] == token_address or pool_info["token1"] == token_address:
                                    pool_contracts.append(
                                        pool_info["pool"] if pool_info.get("pool") else pool_info["pair"]
                                    )

                            if pool_contracts:
                                for pool_contract in pool_contracts:

                                    print("Getting txs")
                                    transactions = self.get_transactions(
                                        from_block=from_block, to_block=to_block,
                                        contract=pool_contract, blockchain=blockchain
                                    )

                                    print("Done getting txs...")

                                    print(f"Number of transactions: {len(transactions)}")
                                    if "v3" in dex:
                                        abi = v3pool_abi
                                    else:
                                        abi = v2pool_abi

                                    # Separate Buyers from Sellers for each transaction and create Dictionary
                                    # representations Wallet address (EOA) as KEY
                                    buyers, sellers = self.map_buyers_and_sellers(blockchain=blockchain, all_entries=transactions,
                                                                                  blacklisted=blacklisted, abi=abi)

                                    # transactions with unwanted accounts filtered out
                                    filtered_transactions = self.filter_transactions(buyers, sellers)

                                    token, _ = Token.objects.get_or_create(
                                        name=contract.token.name,
                                        address=contract.contract
                                    )

                                    print("", token.name)

                                    # Update Database with new wallets and transactions
                                    self.create_database_entry(filtered_transactions=filtered_transactions, token=token,
                                                               chain=contract.chain, timestamp=timestamp,
                                                               percentage=str(percentage), index=index)
                            else:
                                print(f"-------------Pool not found for Token {contract.token.name} - {token_address}")

            contract.processed = True
            contract.save()
            break



















