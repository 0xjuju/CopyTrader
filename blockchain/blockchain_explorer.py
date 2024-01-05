
import asyncio
from decimal import Decimal
from functools import lru_cache
import json
import sys
import time
import traceback
import types

import web3.contract
from websockets import connect

from algorithms.basic_tools import flatten_list
from blockchain.decorators import *
from decouple import config
from eth_utils import event_abi_to_log_topic, to_hex, to_checksum_address
from hexbytes import HexBytes
from web3 import Web3
from web3.auto import w3
from web3.exceptions import BadFunctionCallOutput
from web3._utils.events import get_event_data
from web3.middleware import geth_poa_middleware


class Explorer:

    def __init__(self, chain: str, version: int = 3, use_testnet: bool = False, ):
        """
        :param chain: which chain to explore
        :param version: chain version
        :param use_testnet: mainnet or testnet
        """

        self.chain = chain
        self.use_testnet = use_testnet
        self.version = version

        # Node provider. Initialized from set_connection()
        self.provider_url = None

        self.connection_type = None
        if self.chain == "ethereum" or self.chain == "eth":
            self.connection_type = "goerli" if self.use_testnet else "mainnet"
        elif self.chain == "arbitrum" or self.chain == "arbitrum-one":
            self.connection_type = "arbitrum-mainnet"
        elif self.chain == "avalanche":
            self.connection_type = "avalanche-mainnet"

        # Set Provider URL Based on selected chain, then connect
        self.web3 = self.set_connection()


    def convert_from_hex(self, value: hex) -> int:
        """
        :param value: encoded hex values from transactiond ata
        :return: Inter representation of hex value
        """
        if self.chain == "eth" or self.chain == "ethereum":
            return self.web3.toInt(hexstr=value) // 1000000
        elif self.chain == "binance-smart-chain":
            return self.web3.toInt(hexstr=value) // 1000000000000000000

    @staticmethod
    def convert_to_checksum_address(address: str):

        return to_checksum_address(address)

    def convert_to_checksum_address_from_hex(self, address: hex) -> str:
        """
        Convert address to unique checksum counterpart
        :param address: wallet or contract address
        :return:
        """
        address = address.hex()
        return self.web3.toChecksumAddress('0x' + address[-40:])

    @staticmethod
    def convert_balance(*, balance, decimals: int) -> float:
        """
        Convert long-form integer from transaction to Decimal
        :param balance: wallet balance
        :param decimals: number of decimals to use for balance
        :return: decimal representation of balance
        """

        balance = Decimal(balance)
        return balance / (10 ** decimals)

    def convert_to_hex(self, arg, target_schema):
        """
        :param arg:
        :param target_schema:
        :return:
        """

        output = dict()
        for k in arg:
            if isinstance(arg[k], (bytes, bytearray)):
                output[k] = to_hex(arg[k])
            elif isinstance(arg[k], list) and len(arg[k]) > 0:
                target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
                if target['type'] == 'tuple[]':
                    target_field = target['components']
                    output[k] = self.decode_list_tuple(arg[k], target_field)
                else:
                    output[k] = self.decode_list(arg[k])
            elif isinstance(arg[k], tuple):
                target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
                output[k] = self.decode_tuple(arg[k], target_field)
            else:
                output[k] = arg[k]
        return output

    def custom_filter(self, **kwargs):
        """
        :param kwargs: filter arguments for web3 event filter [from_block, to_block, address...]
        :return: Event filter based on keyword arguments
        """
        excepted_chains = ["eth", "ethereum", "binance-smart-chain"]
        if self.chain in excepted_chains:
            event_filter = self.web3.eth.filter(kwargs)
            return event_filter
        else:
            raise ValueError("Chain not supported for newFilter lookup")

    @staticmethod
    def decode_list(l: list[(bytes, bytearray)]) -> list[hex]:
        """
        Decode list of bytes / bytesarray in hex
        :param l: list of tuples with two values (byte, bytearray)
        :return: list of hex values
        """
        output = l
        for i in range(len(l)):
            if isinstance(l[i], (bytes, bytearray)):
                output[i] = to_hex(l[i])
            else:
                output[i] = l[i]
        return output

    def decode_list_tuple(self, l, target_field):
        """
        :param l:
        :param target_field:
        :return:
        """
        output = l
        for i in range(len(l)):
            output[i] = self.decode_tuple(l[i], target_field)
        return output

    def decode_log(self, data: list[hex], topics: list[hex], abi: str):
        """

        :param data: Encoded data containing specific transcaction information like swap amounts, values, items swapped
        :param topics: EOAs and contracts associated with transaction
        :param abi: Functions of contract
        :return: Type of transaction event and  Transaction metadata
        """
        if abi is not None:
            try:
                topic2abi = self._get_topic2abi(abi)

                log = {
                    'address': None,  # Web3.toChecksumAddress(address),
                    'blockHash': None,  # HexBytes(blockHash),
                    'blockNumber': None,
                    'data': data,
                    'logIndex': None,
                    'topics': [self._get_hex_topic(_) for _ in topics],
                    'transactionHash': None,  # HexBytes(transactionHash),
                    'transactionIndex': None
                }
                print(topic2abi)
                event_abi = topic2abi[log['topics'][0]]
                evt_name = event_abi['name']

                data = get_event_data(w3.codec, event_abi, log)['args']
                target_schema = event_abi['inputs']
                decoded_data = self.convert_to_hex(data, target_schema)

                return evt_name, json.dumps(decoded_data), json.dumps(target_schema)
            except Exception:
                return 'decode error', traceback.format_exc(), None

        else:
            return 'no matching abi', None, None

    def decode_tx(self, address: str, input_data: str, abi: str):
        """
        Decode input data

        :param address: contract address
        :param input_data: encoded data
        :param abi: Application binary Interface str json
        :return:
        """
        if abi is not None:
            try:
                (contract, abi) = self._get_contract(address, abi)
                func_obj, func_params = contract.decode_function_input(input_data)
                target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
                decoded_func_params = self.convert_to_hex(func_params, target_schema)
                return func_obj.fn_name, json.dumps(decoded_func_params), json.dumps(target_schema)

            except:
                e = sys.exc_info()[0]
                return 'decode error', repr(e), None
        else:
            return 'no matching abi', None, None

    def decode_tuple(self, t, target_field):
        output = dict()
        for i in range(len(t)):
            if isinstance(t[i], (bytes, bytearray)):
                output[target_field[i]['name']] = to_hex(t[i])
            elif isinstance(t[i], tuple):
                output[target_field[i]['name']] = self.decode_tuple(t[i], target_field[i]['components'])
            else:
                output[target_field[i]['name']] = t[i]
        return output

    def event_filter(self, **kwargs):
        event = self.web3.eth.filter(kwargs)
        return event

    @staticmethod
    def event_listener(func, **kwargs):

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    func(**kwargs)
                )
            )

        finally:
            loop.close()

    def get_contract_pools(self, contract: web3.contract.Contract, from_block=0, to_block=None, argument_filters=None)\
            -> list[dict]:
        """

        :param contract: Factory contract address
        :param from_block: start block
        :param to_block: end block
        :param argument_filters: query filters
        :return:
        """
        token_pools = list()

        if not to_block:
            to_block = self.web3.eth.block_number

        arguments = dict()

        if argument_filters:
            if isinstance(argument_filters, dict):
                arguments.update(argument_filters)
            else:
                raise TypeError(f"Expecting type Dict, not {type(argument_filters)}")

        print(list(contract.events))
        try:
            pools = contract.events.PoolCreated.createFilter
        except web3.exceptions.ABIEventFunctionNotFound:
            pools = contract.events.PairCreated.createFilter

        events = self._get_logs(pools, fromBlock=from_block, toBlock=to_block, argument_filters=arguments)

        for event in events:
            for pool in event:
                pool_contract = pool["args"]["pool"] if pool["args"].get("pool") else pool["args"]["pair"]

                token_pools.append(
                    {
                        "token0": pool["args"]["token0"],
                        "token1": pool["args"]["token1"],
                        "pool": pool_contract,
                    }
                )

        return token_pools

    @staticmethod
    async def get_event():
        async with connect("wss://goerli.infura.io/ws/v3/26746c91736a449faf4a9db9d6fc7723") as ws:
            await ws.send({"id": 1, "method": "eth_subscribe", "params": ["newHeads"]})
            subscription_response = await ws.recv()
            # you are now subscribed to the event
            # you keep trying to listen to new events (similar idea to longPolling)
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=60)
                    print(json.loads(message))
                    pass
                except Exception as e:
                    print(e)

    def handle_event(self, **kwargs):
        print(self.web3.toJSON(kwargs.get("event")))

    async def loop_logs(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_all_entries():
                self.handle_event(event=event)

            await asyncio.sleep(poll_interval)

    async def check_balance(self, wallet_address, contract, abi, poll_interval, old_balance, handle):
        while True:
            balance = self.get_balance_of_token(wallet_address, contract, abi)
            if balance != old_balance:
                print("NOT EQUAL")
                handle()
                break
            await asyncio.sleep(poll_interval)

    def filter_account(self, address, start_block, end_block):
        return self.web3.eth.filter({"fromBlock": start_block, "toBlock": end_block, "address": address})

    @check_keyword_args
    def filter_contract(self, *, max_chunk=None, **kwargs):
        """
        :param max_chunk: Max block size to use for block range
        :param kwargs: Filter params for query
        :return:
        """
        contract_address = self.web3.toChecksumAddress(kwargs["address"])
        from_block = kwargs.get("fromBlock")
        to_block = kwargs.get("toBlock")

        # BSC Scan is rate-limited 5000 txs for block-range per query
        if self.chain == "binance-smart-chain" and isinstance(max_chunk, int) and to_block - from_block > max_chunk:
            event_filter_list = self.get_paginated_event_filters(max_chunk=max_chunk, **kwargs)
            return event_filter_list

        else:
            event_filter = self.web3.eth.filter({
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": contract_address,
            })

            return event_filter.get_all_entries()

    def get_address_from_block(self, block_number):
        block = self.get_block(block_number)
        return block

    @lru_cache(maxsize=None)
    def _get_contract(self, address, abi):
        """
        This helps speed up execution of decoding across a large dataset by caching the contract object
        It assumes that we are decoding a small set, on the order of thousands, of target smart contracts
        """
        if isinstance(abi, str):
            abi = json.loads(abi)

        contract = w3.eth.contract(address=self.web3.toChecksumAddress(address), abi=abi)
        return contract, abi

    def get_contract(self, token_contract_address, abi):
        # token_contract_address = self.web3.toChecksumAddress(token_contract_address)
        contract = self.web3.eth.contract(token_contract_address, abi=abi)
        return contract

    def get_contract_abi(self, contract):
        return self.web3.eth.contract(contract=contract).abi

    def get_balance_of_token(self, wallet_address: str, token_contract_address: str, abi: str) -> float:
        """
        :param wallet_address: EOA address
        :param token_contract_address: Contract address
        :param abi: ABI of contract
        :return: balance of EOA
        """

        wallet_address = self.web3.toChecksumAddress(wallet_address)
        token_contract_address = self.web3.toChecksumAddress(token_contract_address)
        contract = self.get_contract(token_contract_address, abi)
        while True:
            try:
                balance = contract.functions.balanceOf(wallet_address).call()

            # catch occasional API error
            except BadFunctionCallOutput:
                time.sleep(10)
                continue

            else:
                break

        return balance  # / (10 ** 18)

    def get_block(self, block_num=None):
        if block_num:
            return self.web3.eth.get_block(block_num)
        else:
            return self.web3.eth.get_block('latest')

    def get_last_n_blocks(self, n: int):
        latest_block = self.get_block()["number"]
        start = latest_block - n
        return start, latest_block

    def _get_logs(self, filter_object, **kwargs):
        """
        Recursive get_logs function to handle -32005 error when query returns too many results.
        Split blocks in half until all queries are completed successfully

        :param kwargs: query parameters for blockchain query [toBlock, fromBlock, address, ...]
        :return: get_logs query
        """

        try:  # Catch error when quert limit is exceeded
            try:  # createFilter requires individual keyword arguments, so TypeError expected to convert arguemnt type
                logs = filter_object(kwargs)
            except TypeError as e:
                # Check if contract.createFilter function inside error message.
                if "createFilter" in str(e):
                    logs = filter_object(**kwargs).get_all_entries()
                else:
                    raise TypeError(e)

            yield logs

        except ValueError as e:
            if "-32005" in str(e):
                print(e)
                start_block = kwargs["fromBlock"]
                end_block = kwargs["toBlock"]
                if abs(start_block - end_block) == 0:
                    raise ValueError("Block Range reduced to 0. Infinite recursion...")

                # Split blocks in half
                start1, stop1 = start_block, start_block + abs(start_block - end_block) // 2
                start2, stop2 = stop1 + 1, end_block
                # print(f"Number of Blocks: {abs(start_block - end_block):,}")
                # Recursively break query into two calls, until each log returns less tha 10,000 results
                yield from self._get_logs(filter_object, fromBlock=start1, toBlock=stop1, address=kwargs.get("address"))
                yield from self._get_logs(filter_object, fromBlock=start2, toBlock=stop2, address=kwargs.get("address"))
            else:
                raise ValueError(e)

    # @check_keyword_args
    def get_logs(self, *, max_chunk=None, **kwargs):
        """
        :param max_chunk: max block size to filter
        :param kwargs: Filter params for log data. fromBlock, toBlock, address...
        :return: Event log filter
        """

        from_block = kwargs.get("fromBlock")
        to_block = kwargs.get("toBlock")
        block_range = to_block - from_block

        if max_chunk and from_block and to_block and block_range > max_chunk:
            logs = self.get_paginated_event_filters(max_chunk=max_chunk, **kwargs)
        else:
            logs = self._get_logs(self.web3.eth.get_logs, **kwargs)

        if isinstance(logs, types.GeneratorType):
            logs = flatten_list(list(logs))

        return logs

    def get_paginated_event_filters(self, *, max_chunk, **kwargs):
        """
        :param max_chunk: Max block range
        :param kwargs: Query params for filter
        :return: list of filtered transaction between block range
        """
        event_filter_list = list()
        from_block = kwargs["fromBlock"]
        to_block = kwargs["toBlock"]

        # Create list of paginated blocks incremented by the rate limit
        pages = self.paginate(from_block, to_block, increment=max_chunk)

        for index, page in enumerate(pages):
            time.sleep(0.5)
            # arbitrum-one network needs to use get_logs. HTTPS does not support eth_newFilter

            # if self.chain == "arbitrum-one" or self.chain == "polygon-pos":
            event_filter = self.get_logs(
                fromBlock=page[0],
                toBlock=page[1],
                address=kwargs["address"],
            )
            entries = event_filter

            # else:
            #     event_filter = self.web3.eth.filter({
            #         "fromBlock": page[0],
            #         "toBlock": page[1],
            #         "address": kwargs["address"],
            #     })
            #     entries = event_filter.get_all_entries()

            # Create single list of all event filters
            for entry in entries:
                event_filter_list.append(entry)

        return event_filter_list

    @lru_cache(maxsize=None)
    def _get_hex_topic(self, t):
        hex_t = HexBytes(t)
        return hex_t

    def get_swap_events(self, pair_contract, from_block, to_block):

        event_filter = pair_contract.events.Swap.createFilter(fromBlock=from_block, toBlock=to_block, topics=[1, 2])
        # events = self._get_logs(event_filter, fromBlock=from_block, toBlock=to_block)
        return event_filter

    def get_transaction_hash_data(self, transaction_hash):
        return self.web3.eth.get_transaction(transaction_hash)

    @lru_cache(maxsize=None)
    def _get_topic2abi(self, abi):
        if isinstance(abi, str):
            abi = json.loads(abi)

        event_abi = [a for a in abi if a['type'] == 'event']
        topic2abi = {event_abi_to_log_topic(_): _ for _ in event_abi}
        return topic2abi


    @transaction_not_found_exception
    def get_transaction_receipt(self, transaction_hash):
        return self.web3.eth.get_transaction_receipt(transaction_hash)

    @staticmethod
    def paginate(start, stop, increment: int):
        """
        :param start:
        :param stop:
        :param increment:
        :return:
        """
        ranges = list()
        while start < stop:
            ranges.append(
                (start, start + increment)
            )

            start += increment
        return ranges

    def set_connection(self):

        map_rpc = {
            "eth": f"https://{self.connection_type}.infura.io/v{self.version}/{config('INFURA_ID')}",
            "ethereum": f"https://{self.connection_type}.infura.io/v{self.version}/{config('INFURA_ID')}",
            "arbitrum": f"https://{self.connection_type}.infura.io/v{self.version}/{config('INFURA_ID')}",
            "arbitrum-one": f"https://{self.connection_type}.infura.io/v{self.version}/{config('INFURA_ID')}",
            "binance-smart-chain": "https://bsc-dataseed.binance.org/",
            "polygon-pos": config("INFURA_POLYGON_RPC_URL"),
            "avalanche": f"https://{self.connection_type}.infura.io/v{self.version}/{config('INFURA_ID')}",
        }

        rpc_url = map_rpc.get(self.chain)

        if rpc_url is None:
            raise ValueError(f"RPC not identified. Value: {self.chain}")

        connection = Web3(Web3.HTTPProvider(rpc_url))
        self.provider_url = rpc_url
        # Must set middleware to explore blocks on bsc using web3
        if self.chain == "binance-smart-chain" or self.chain == "polygon-pos":
            connection.middleware_onion.inject(geth_poa_middleware, layer=0)
        return connection

    def wallets_in_blocks(self, wallets: list[str], num_blocks=10000):
        pass









