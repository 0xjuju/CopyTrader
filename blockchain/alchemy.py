from functools import lru_cache
from hexbytes import HexBytes
import json
import requests
import time
import traceback
import types

from algorithms.basic_tools import flatten_list
import decouple
from eth_utils import event_abi_to_log_topic, to_hex
import web3
from web3 import Web3
from web3._utils.events import get_event_data
from web3.contract import Contract
from web3.exceptions import ABIEventFunctionNotFound


class Blockchain:
    def __init__(self, chain: str):

        self.API_KEY = decouple.config("ALCHEMY_API_KEY")
        self.chain = chain
        self.chain_map = self.chain_to_rpc(chain)

        self.url = f"https://{self.chain_map}-mainnet.g.alchemy.com/v2/{self.API_KEY}"
        self.w3 = Web3(Web3.HTTPProvider(self.url))

    @lru_cache(maxsize=None)
    def _get_hex_topic(self, t):
        hex_t = HexBytes(t)
        return hex_t

    @lru_cache(maxsize=None)
    def _get_topic2abi(self, abi):
        if isinstance(abi, str):
            abi = json.loads(abi)

        event_abi = [a for a in abi if a['type'] == 'event']
        topic2abi = {event_abi_to_log_topic(_): _ for _ in event_abi}
        return topic2abi

    def _query_filter(self, filter_object, **kwargs):
        """
        Recursive get_logs function to handle -32005 error when query returns too many results.
        Split blocks in half until all queries are completed successfully

        :param kwargs: query parameters for blockchain query [toBlock, fromBlock, address, ...]
        :return: get_logs query
        """

        try:
            logs = filter_object(**kwargs).get_all_entries()
            yield logs

        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                try:
                    logs = filter_object(kwargs)
                    yield logs
                except ValueError as e:
                    if "-32602" in str(e):
                        self._recursive_query(filter_object, kwargs)
            else:
                raise TypeError(e)

        except ValueError as e:  # Catch error when query limit is exceeded
            if "-32602" in str(e):
                self._recursive_query(filter_object, kwargs)
            else:
                raise ValueError("Diff---", e)

    def _recursive_query(self, filter_object, params):
        start_block = params["fromBlock"]
        end_block = params["toBlock"]
        if abs(start_block - end_block) == 0:
            raise ValueError("Block Range reduced to 0. Infinite recursion...")

        # Split blocks in half
        start1, stop1 = start_block, start_block + abs(start_block - end_block) // 2
        start2, stop2 = stop1 + 1, end_block
        # print(f"Number of Blocks: {abs(start_block - end_block):,}")
        # Recursively break query into two calls, until each log returns less tha 10,000 results
        yield from self._query_filter(filter_object, fromBlock=start1, toBlock=stop1, address=params.get("address"))
        yield from self._query_filter(filter_object, fromBlock=start2, toBlock=stop2, address=params.get("address"))

    @staticmethod
    def chain_to_rpc(chain: str) -> str:
        rpc_list = {
            "ethereum": f"eth",
            "arbitrum-one": "arb",
            "polygon-pos": "polygon",
        }
        return rpc_list[chain]

    def checksum_address(self, address: str) -> str:
        """
        Convert address to checksum address, capitalizing some characters for error-handling

        :param address: blockchain address
        :return: checksum address
        """
        return self.w3.to_checksum_address(address)

    def convert_to_checksum_address_from_hex(self, address: hex) -> str:
        """
        Convert address to unique checksum counterpart
        :param address: wallet or contract address
        :return:
        """
        address = address.hex()
        return self.w3.to_checksum_address('0x' + address[-40:])

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
                event_abi = topic2abi[log['topics'][0]]
                evt_name = event_abi['name']

                data = get_event_data(self.w3.codec, event_abi, log)['args']
                target_schema = event_abi['inputs']
                decoded_data = self.convert_to_hex(data, target_schema)

                return evt_name, json.dumps(decoded_data), json.dumps(target_schema)
            except Exception:
                return 'decode error', traceback.format_exc(), None

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

    @lru_cache(maxsize=None)
    def get_contract(self, address: str, abi: str) -> web3.contract.Contract:
        """
        This helps speed up execution of decoding across a large dataset by caching the contract object
        It assumes that we are decoding a small set, on the order of thousands, of target smart contracts
        """
        if isinstance(abi, str):
            abi = json.loads(abi)
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(address), abi=abi)

        return contract

    def get_factory_pools(self, contract: web3.contract.Contract, from_block=0, to_block=None, argument_filters=None)\
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
            to_block = self.w3.eth.block_number

        arguments = dict()

        if argument_filters:
            if isinstance(argument_filters, dict):
                arguments.update(argument_filters)
            else:
                raise TypeError(f"Expecting type Dict, not {type(argument_filters)}")

        try:
            pools = contract.events.PoolCreated.create_filter

        except web3.exceptions.ABIEventFunctionNotFound:
            events = [str(i) for i in contract.events]

            if "<class 'web3._utils.datatypes.Pool'>" in events:
                pools = contract.events.Pool.create_filter

            elif "<class 'web3._utils.datatypes.PairCreated'>" in events:
                pools = contract.events.PairCreated.create_filter

            else:
                print(list(contract.events))
                raise web3.exceptions.ABIEventFunctionNotFound

        events = self._query_filter(pools, fromBlock=from_block, toBlock=to_block, argument_filters=arguments)

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

    def get_block(self, block_num=None):

        if block_num is None:
            block_num = self.w3.eth.block_number

        return self.w3.eth.get_block(block_num)

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
            logs = self._query_filter(self.w3.eth.get_logs, **kwargs)

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

    def is_connected(self) -> bool:
        return self.w3.isConnected()


class Webhook:
    def __init__(self):
        self.WEBHOOK_URL = "https://dashboard.alchemy.com/api/"
        self.WEBHOOK_KEY = decouple.config("ALCHEMY_WEBHOOK_KEY")

        self.networks = {
            "ethereum": "ETH_MAINNET",
            "arbitrum-one": "ARB_MAINNET",
            "polygon-pos": "MATIC_MAINNET"
        }

        self.WEBHOOK_OPTIONS = [
            "ADDRESS_ACTIVITY",
            "MINED_TRANSACTION",
            "GRAPHQL",
            "DROPPED_TRANSACTION",
            "NFT_ACTIVITY",
            "NFT_METADATA_UPDATE"
        ]

    def _make_request(self,endpoint: str, chain: str, webhook_type: str, payload_opts: dict) -> dict:
        network = self.networks[chain]

        url = self.WEBHOOK_URL + endpoint
        if webhook_type not in self.WEBHOOK_OPTIONS:
            raise ValueError(f"{webhook_type} not a valid option from {self.WEBHOOK_OPTIONS}")

        payload = {
            "network": network,
            "webhook_type": webhook_type,
            "webhook_url": None
        }
        if payload_opts:
            payload.update(payload_opts)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.post(url, json=payload, headers=headers)

        return response.json()

    def create_wallet_activity_webhook(self, chain: str, webhook_type: str, address_list: list[str]) -> None:
        payload = {"addresses": address_list}

        self._make_request("create-webhook", chain=chain, webhook_type=webhook_type, payload_opts=payload)

    def get_address_list_from_webhook(self, webhook_id: str, limit=100, page_cursor=0) -> dict:
        url = f"https://dashboard.alchemy.com/api/webhook-addresses?webhook_id={webhook_id}&limit={limit}&after={page_cursor}"

        headers = {
            "accept": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def get_all_webhooks(self) -> dict:
        url = self.WEBHOOK_URL + "team-webhooks"
        headers = {
            "accept": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY
        }
        response = requests.get(url, headers=headers)

        return response.json()

    def replace_webhook_address_list(self, webhook_id: str, address_list: list[str]):
        url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
        payload = {
            "webhook_id": webhook_id,
            "addresses": address_list,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.put(url, json=payload, headers=headers)
        print(response)







