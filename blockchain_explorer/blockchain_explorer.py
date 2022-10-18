
import asyncio
import time
from functools import lru_cache
import sys
import traceback
from decimal import Decimal
import json

from blockchain_explorer.decorators import *
from decouple import config
from eth_utils import event_abi_to_log_topic, to_hex
from hexbytes import HexBytes
from web3 import Web3
from web3.auto import w3
from web3.exceptions import BadFunctionCallOutput
from web3._utils.events import get_event_data
from web3.middleware import geth_poa_middleware


class Explorer:
    def __init__(self, chain: str):
        """
        :param chain: explore either ethereum (eth) or binance smart chain (bsc) blockchain, otherwise error will be
        raised
        """

        self.chain = chain

        # Set Provider URL Based on selected chain, then connect
        self.web3 = self.set_connection()

        if self.chain == "bsc":  # Must set middleware to explore blocks on bsc using web3
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def convert_from_hex(self, value: hex) -> int:
        """
        :param value: encoded hex values from transactiond ata
        :return: Inter representation of hex value
        """
        if self.chain == "eth" or self.chain == "ethereum":
            return self.web3.toInt(hexstr=value) // 1000000
        elif self.chain == "bsc":
            return self.web3.toInt(hexstr=value) // 1000000000000000000

    def convert_to_checksum_address(self, address: hex) -> str:
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
        excepted_chains = ["eth", "ethereum", "bsc"]
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
        :return: Type of transcation event and  Transaction metadata
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

    def decode_tx(self, address, input_data, abi):
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
            print(balance, old_balance)
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
        if self.chain == "bsc" and isinstance(max_chunk, int) and to_block - from_block > max_chunk:
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
        contract = self.get_contract(token_contract_address, abi)
        while True:
            try:
                balance = contract.functions.balanceOf(wallet_address).call()

            # catch occasional API error
            except BadFunctionCallOutput:
                time.sleep(20)
                continue

            else:
                break

        return balance / (10 ** 18)

    def get_block(self, block_number):
        return self.web3.eth.get_block(block_number)

    @check_keyword_args
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
            logs = self.web3.eth.get_logs(kwargs)

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

            # polygon network needs to use get_logs. HTTPS does not support eth_newFilter
            if self.chain == "polygon":
                event_filter = self.get_logs(
                    fromBlock=page[0],
                    toBlock=page[1],
                    address=kwargs["address"],
                )
                entries = event_filter

            else:
                event_filter = self.web3.eth.filter({
                    "fromBlock": page[0],
                    "toBlock": page[1],
                    "address": kwargs["address"],
                })
                entries = event_filter.get_all_entries()

            # Create single list of all event filters
            for entry in entries:
                event_filter_list.append(entry)

        return event_filter_list

    @lru_cache(maxsize=None)
    def _get_hex_topic(self, t):
        hex_t = HexBytes(t)
        return hex_t

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
        ranges = list()
        while start < stop:
            ranges.append(
                (start, start + increment - 1)
            )
            start += increment
        return ranges

    def set_connection(self):
        map_rpc = {
            "eth": config("INFURA_RPC_URL"),
            "ethereum": config("INFURA_RPC_URL"),
            "bsc": "https://bsc-dataseed.binance.org/",
            "polygon": config("INFURA_POLYGON_RPC_URL"),
        }
        connection = Web3(Web3.HTTPProvider(map_rpc.get(self.chain)))
        return connection









