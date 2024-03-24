from collections import defaultdict, Counter
from datetime import datetime, timedelta
import logging
import time

from algorithms.token_dataset_algos import percent_difference_from_dataset
from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan
from blockchain.class_models import BlockRange, CoingeckoPriceBreakout, Swap
from blockchain.models import Chain, ABI, FactoryContract
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address
# from django.db.models import Q
from wallets.models import Bot, Transaction, Wallet, Token
from web3 import Web3


logging.basicConfig(level=logging.INFO)


class Updater:

    @staticmethod
    def contract_and_address_validated(checked_topics: list[str], blacklisted: list[str], blockchain: Blockchain)\
            -> bool:
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
        else:
            return False

    @staticmethod
    def create_database_entry(filtered_transactions: list[Swap], token: Token, chain: str,
                              percentage: str, index: int) -> None:
        """
        :param filtered_transactions: transaction data with possible bots / unwanted accounts filtered out
        :param token: Token model
        :param chain: chain
        :param percentage: percentage increase from price breakout
        :param index: Index for batch
        """

        # Previous transactions fom database. Used to check against duplciate entries
        all_transactions = Transaction.objects.all()

        for transaction_data in filtered_transactions:
            address = transaction_data.sender

            # raw tx data
            transaction = transaction_data.transaction

            amount = transaction_data.amount / (10 ** 18)

            wallet, _ = Wallet.objects.get_or_create(address=address)

            if wallet.token.filter(address=token.address).exists() is False:
                wallet.token.add(token)

            transaction_hash = transaction["transactionHash"].hex()
            if not all_transactions.filter(transaction_hash=transaction_hash).exists():
                timestamp = transaction_data.timestamp
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

    @staticmethod
    def create_block_range(duration: int, timestamp: int, explorer: Blockscan) -> BlockRange:

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
        if before_breakout_timestamp < days_ago_116 or three_days_into_breakout_timestamp < days_ago_116:
            raise ValueError(f" timstamps should never be less than 116 days before now {before_breakout_timestamp},"
                             f" {three_days_into_breakout_timestamp}")

        # If block is not found, error message returned. Catch Value error when converting to integer
        return BlockRange(from_block=int(from_block), to_block=int(to_block))

    @staticmethod
    def determine_price_breakouts(diffs: list[list[float]], timestamps: list[int], percent_threshold: float)\
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
            start_day = None
            if d[0] > percent_threshold:
                start_day = 1
            elif d[1] > percent_threshold:
                start_day = 3
            elif d[2] > percent_threshold:
                start_day = 7

            # only append data if a start date of price increase is found
            if start_day:
                print(d, datetime.fromtimestamp(timestamps[index]))

                # largest move percentage within the three timeframes. Used to avoid duplicate data
                largest_price_move = max(d)
                price_breakouts.append(
                    CoingeckoPriceBreakout(day=start_day, timestamp=timestamps[index], largest_price_move=largest_price_move)
                )

        return price_breakouts

    @staticmethod
    def filter_transactions(buyers: dict[str, list[Swap]], explorer: Blockscan, blockchain: Blockchain,
                            token_address: str) -> list[Swap]:
        """

        :param buyers: List of buyers of token
        :param explorer: etherscan
        :param blockchain: main blockchain explorer
        :param token_address: Address of token
        :return:
        """

        # Loop through buyers and sellers to create list of transaction excluding ones likely done by bots
        filtered_transactions = list()
        for buyer, swaps in buyers.items():

            # Total amount of all swaps for buyer
            total = sum([i.amount for i in swaps])

            # Get future block of tx 3 days into future
            future_timestamp = (datetime.fromtimestamp(swaps[0].timestamp) + timedelta(days=3)).timestamp()
            future_block = explorer.get_block_by_timestamp(int(future_timestamp),
                                                           look_for_previous_block_if_error=True)

            # Get balance of token for wallet, if still holding at least half, wallet is less likely a bot
            # Also filters out users who buy and sell before token actually increases
            balance = blockchain.get_balance_of_token(token_address, buyer, block_number=future_block)
            if balance >= total / 2:
                for swap in swaps:
                    swap.sender = buyer
                    filtered_transactions.append(swap)

        # Number of tx for each account
        tx_count = Counter(i.sender for i in filtered_transactions)
        # Filter accounts to ones with less than 4 transactions for this range of block
        filtered_transactions = [i for i in filtered_transactions if tx_count[i.sender] <= 4]
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

        print(f"Using these factory contracts on {blockchain.chain} {[f'{i.name}' for i in factory_contracts]}")
        print(f"> Found the following pools from each contract")
        for factory in factory_contracts:
            contract = blockchain.get_contract(factory.address, factory.abi)

            pools[factory.chain][factory.name] = {
                "pools": list(),
                "abi": factory.abi
            }

            get_pools = blockchain.get_factory_pools(contract, argument_filters={"token1": token_address})
            if not get_pools:
                get_pools = blockchain.get_factory_pools(contract, argument_filters={"token0": token_address})

            str_pools = [f"{i}\n" for i in get_pools]
            print(f"----- > {factory.name} Pools:\n {''.join(str_pools)}")
            for pool in get_pools:
                pools[factory.chain][factory.name]["pools"].append(pool)

        return pools

    @staticmethod
    def get_pool_contracts(pools: dict[str, dict], token: Address) -> list[str]:
        dex_list = pools[token.chain]
        pool_contracts = list()
        for dex, data in dex_list.items():
            # factory_abi = data["abi"]
            for pool_info in data["pools"]:
                pool = pool_info["pool"] if pool_info.get("pool") else pool_info["pair"]
                pool_contracts.append(
                    pool
                )

        return pool_contracts

    @staticmethod
    def get_prices_data(contract_address: str, chain: str) -> tuple[list, list]:
        """
        :param contract_address: contract address of token
        :param chain: token chain
        :return: list of timestamps and related prices
        """

        # Get last 100 days of prices for token
        price_data = GeckoClient().get_market_chart_by_contract(contract_address=contract_address, chain=chain)
        if price_data:
            price_data = price_data["prices"]
            timestamps = [i[0] / 1000 for i in price_data]
            prices = [i[1] for i in price_data]
        else:
            timestamps, prices = list(), list()

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

        if blockchain.chain == "polygon-pos":
            max_chunk = 3500

        transactions = blockchain.get_logs(max_chunk=max_chunk, address=address,
                                           fromBlock=from_block, toBlock=to_block)
        return transactions

    def map_buyers_and_sellers(self, decimals: int, blockchain: Blockchain, all_entries, blacklisted) -> (
            defaultdict[list[Swap]],
            defaultdict[list[Swap]],
            ):
        """
        :param decimals: decimals of token
        :param blockchain: Blockchain explorer
        :param all_entries: list of transaction from given timeframe
        :param blacklisted: Known automated addresses
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

                    log_data = blockchain.get_event(data, topics, "Swap")

                    if log_data:

                        log_data = log_data.logs
                        block = transaction["blockNumber"]
                        timestamp = blockchain.get_block(block)["timestamp"]

                        try:
                            # Uniswap V3 log data has different vs v2
                            amount0 = log_data["amount0"]
                            amount1 = log_data["amount1"]

                            if amount0 > 0:
                                amount = abs(blockchain.convert_raw_balance(amount1, decimals))
                                buyers[from_address].append(Swap(transaction, timestamp, "buy", amount))

                            elif amount0 < 0:
                                sellers[from_address].append(Swap(transaction, timestamp, "sell", amount1))

                        except KeyError:
                            # Try for V3 first. If Key Error, try V2 syntax
                            if from_address == log_data["to"] and log_data["amount0Out"] > 0:
                                sellers[from_address].append(Swap(transaction, timestamp, "sell", log_data["amount0Out"]))

                            elif from_address == log_data["to"] and log_data["amount1Out"] > 0:
                                amount = blockchain.convert_raw_balance(log_data["amount1Out"], decimals)
                                buyers[from_address].append(Swap(transaction, timestamp, "buy", amount))

                            # We want to classify as either BUYER or SELLER always using these criteria
                            else:
                                raise Exception(f"Unidentified error\n {transaction['transactionHash'].hex(), log_data}")

        return buyers, sellers

    def update(self, percent_threshold: float):
        chains = Chain.objects.values_list("name", flat=True)

        contracts = Address.objects.filter(chain__in=chains)\
            .filter(processed=False)\
            .filter(
            token__price_change_7d__gte=percent_threshold
        )

        print("Number of Contracts ", len(contracts))

        pools = dict()

        for contract in contracts:
            blockchain = Blockchain(contract.chain)
            blockscan = Blockscan(contract.chain)

            print(f"Name of Token we are analyzing is {contract.token.name}")

            print("Converting token contract to Checksum Address...")
            token_contract = blockchain.checksum_address(contract.contract)
            print(f"Token changed from {contract.contract} to {token_contract}")

            print(f" > Now getting all pools that contain {contract.token.name}")
            pools.update(self.get_dex_pairs(blockchain, token_contract))

            print(" > Get contract address for each pool...")
            pool_contracts = self.get_pool_contracts(pools, contract)
            print(f"{len(pool_contracts)} contracts: {pool_contracts}")

            print(f" > Getting timestamps and prices from Coingecko for the given contract...\n")
            timestamps, prices = self.get_prices_data(contract.contract, contract.chain)
            print(f" > {len(prices)} results. In the format: (Timestamp, Price)\n")
            print(list(zip([f"{datetime.fromtimestamp(i)}" for i in timestamps], prices)))

            print(" > Calculate percentage difference of each days' price relative to the next day, 3rd, and 7th\n")
            diffs = percent_difference_from_dataset(prices)
            print([f"({i[0]:,.2f}% 1 day, {i[1]:,.2f}% 3 days, {i[2]:,.2f}%) 7 days" for i in diffs])

            print(f"\n > Determine which days have prices that increased by at least {percent_threshold}%\n")
            price_breakouts = self.determine_price_breakouts(diffs, timestamps, percent_threshold)

            print("Looping through each day, creating a block range before price breakout started\n")
            for index, coingecko_breakout in enumerate(price_breakouts):
                duration = coingecko_breakout.day
                timestamp = coingecko_breakout.timestamp
                percentage = coingecko_breakout.largest_price_move

                block_data = self.create_block_range(duration, timestamp, blockscan)
                from_block = block_data.from_block
                to_block = block_data.to_block

                from_block_date = blockchain.get_block_date(from_block)
                to_block_date = blockchain.get_block_date(to_block)

                print(f"Block Range {from_block}-{to_block} ({from_block_date} to {to_block_date})")
                print(f"For timestamp: {datetime.fromtimestamp(timestamp)} + {duration} days")
                print(f"{abs(from_block - to_block)} total blocks")
                print(" > -----")

                print(" > Get batch of transactions for each day there was a significant appreciation in price")
                for pool_contract in pool_contracts:

                    print(f"Recursively splitting blocks in chunks of 10k for {pool_contract} This could take a while")
                    transactions = self.get_transactions(
                        from_block=from_block, to_block=to_block,
                        contract=pool_contract, blockchain=blockchain
                    )

                    if transactions:
                        print(f"Found {len(transactions)} transactions in this block range")

                        print(f"Separating transactions from buyers and sellers for {contract.token.name} token")
                        print("Addresses that are blacklisted or have code associated with it are filtered out.")

                        buyers, sellers = self.map_buyers_and_sellers(
                            blockchain=blockchain, all_entries=transactions, blacklisted=[], decimals=contract.decimals
                        )

                        print(f" > Found {len(buyers)} different Buyers and {len(sellers)} different Sellers")

                        print("Continue to filter transactions based on the following conditions")
                        print("\t > Buyers holds at least half of the original token 3 days later")
                        print("\t > Account doesn't have less than 5 transactions for the block range")

                        filtered_transactions = self.filter_transactions(buyers, blockscan, blockchain,
                                                                            contract.contract)

                        print(f"Number of buyers after filters: {len(filtered_transactions)}")

                        token, _ = Token.objects.get_or_create(
                            name=contract.token.name,
                            address=contract.contract
                        )

                        # Update Database with new wallets and transactions
                        self.create_database_entry(filtered_transactions=filtered_transactions, token=token,
                                                      chain=contract.chain, percentage=str(percentage), index=index)

                        print(f"{len(filtered_transactions)} wallets that bought {contract.token.name} created!!!!!!!")

                print(" > ---------------------------------------------------------------------------------------")
                print(" > ---------------------------------------------------------------------------------------")
                print(" > ---------------------------------------------------------------------------------------")

            transactions = Transaction.objects.filter(token_in=contract.token.name)
            print(f"Done. {transactions.count()} total transactions saved for {contract.token.name} on {contract.chain}")
            contract.processed = True
            contract.save()





















