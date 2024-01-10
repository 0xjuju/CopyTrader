from functools import lru_cache
import time
import json
import types

from algorithms.basic_tools import flatten_list
from decouple import config
import web3
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ABIEventFunctionNotFound


class Blockchain:
    def __init__(self, chain: str):

        self.API_KEY = config("ALCHEMY_API_KEY")
        self.chain = chain
        self.chain_map = self.chain_to_rpc(chain)

        self.url = f"https://{self.chain_map}-mainnet.g.alchemy.com/v2/{self.API_KEY}"
        self.w3 = Web3(Web3.HTTPProvider(self.url))

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
        return self.w3.toChecksumAddress(address)

    def _query_filter(self,filter_object, **kwargs):
        """
        Recursive get_logs function to handle -32005 error when query returns too many results.
        Split blocks in half until all queries are completed successfully

        :param kwargs: query parameters for blockchain query [toBlock, fromBlock, address, ...]
        :return: get_logs query
        """

        try:  # Catch error when query limit is exceeded
            logs = filter_object(**kwargs).get_all_entries()
            yield logs

        except TypeError as e:
            if "unexpected keyword argument 'fromBlock'" in str(e):
                logs = filter_object(kwargs)
                yield logs
            else:
                raise TypeError(e)

        except ValueError as e:
            if "-32602" in str(e):
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
                yield from self._query_filter(filter_object, fromBlock=start1, toBlock=stop1, address=kwargs.get("address"))
                yield from self._query_filter(filter_object, fromBlock=start2, toBlock=stop2, address=kwargs.get("address"))
            else:
                raise ValueError(e)

    @lru_cache(maxsize=None)
    def _get_contract(self, address: str, abi: str) -> web3.contract.Contract:
        """
        This helps speed up execution of decoding across a large dataset by caching the contract object
        It assumes that we are decoding a small set, on the order of thousands, of target smart contracts
        """
        if isinstance(abi, str):
            abi = json.loads(abi)
        contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(address), abi=abi)

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
            pools = contract.events.PoolCreated.createFilter

        except web3.exceptions.ABIEventFunctionNotFound:
            events = [str(i) for i in contract.events]

            if "<class 'web3._utils.datatypes.Pool'>" in events:
                pools = contract.events.Pool.createFilter

            elif "<class 'web3._utils.datatypes.PairCreated'>" in events:
                pools = contract.events.PairCreated.createFilter

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






