
# import asyncio
from functools import lru_cache
import json
import sys
import traceback
from decimal import Decimal
import json

from blockchain_explorer.decorators import transaction_not_found_exception
from decouple import config
from eth_utils import event_abi_to_log_topic, to_hex
from hexbytes import HexBytes
from web3 import Web3
from web3.auto import w3
from web3._utils.abi import exclude_indexed_event_inputs, get_abi_input_names, get_indexed_event_inputs, normalize_event_input_types
from web3._utils.events import get_event_data
from web3.exceptions import TransactionNotFound
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

        self.METAMASK_ROUTER = "0x881d40237659c251811cec9c364ef91dc08d300c"
        self.ONEINCH_ROUTER = "0x11111112542d85b3ef69ae05771c2dccff4faa26"
        self.MEVBOT_ROUTER = "0x98c3d3183c4b8a650614ad179a1a98be0a8d6b8e"
        self.UNISWAP_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        self.UNISWAP_ROUTER2 = "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45"

        self.ABI = self.base_contract_abi()

    @staticmethod
    def base_contract_abi():
        ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'
        return json.loads(ABI)

    def convert_from_hex(self, value):
        if self.chain == "eth" or self.chain == "ethereum":
            return self.web3.toInt(hexstr=value) // 1000000
        elif self.chain == "bsc":
            return self.web3.toInt(hexstr=value) // 1000000000000000000

    def convert_to_checksum_address(self, address):
        address = address.hex()
        return self.web3.toChecksumAddress('0x' + address[-40:])

    @staticmethod
    def convert_balance_to_eth(*, balance, decimals: int) -> Decimal:
        balance = Decimal(balance)
        return Decimal(balance / (10 ** decimals))

    def convert_to_hex(self, arg, target_schema):
        """
        utility function to convert byte codes into human readable and json serializable data structures
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
    def decode_list(l):
        output = l
        for i in range(len(l)):
            if isinstance(l[i], (bytes, bytearray)):
                output[i] = to_hex(l[i])
            else:
                output[i] = l[i]
        return output

    def decode_list_tuple(self, l, target_field):
        output = l
        for i in range(len(l)):
            output[i] = self.decode_tuple(l[i], target_field)
        return output

    def decode_log(self, data, topics, abi):
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

    def filter_account(self, address, start_block, end_block):
        return self.web3.eth.filter({"fromBlock": start_block, "toBlock": end_block, "address": address})

    def filter_contract(self, *, contract_address, from_block, to_block):
        contract = self.web3.toChecksumAddress(contract_address)

        event_filter = self.web3.eth.filter({
            "fromBlock": from_block,
            "toBlock": to_block,
            "address": contract,
        })
        return event_filter

    def get_address_from_block(self, block_number, address):
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

    def get_contract(self, token_contract_address):
        token_contract_address = self.web3.toChecksumAddress(token_contract_address)
        contract = self.web3.eth.contract(token_contract_address, abi=self.ABI)
        return contract

    def get_contract_abi(self, contract):
        return self.web3.eth.contract(contract=contract).abi

    def get_balance_of_token(self, wallet_address: str, token_contract_address: str):
        wallet_address = self.web3.toChecksumAddress(wallet_address)
        contract = self.get_contract(token_contract_address)

        raw_balance = contract.functions.balanceOf(wallet_address).call()

        value = self.web3.fromWei(raw_balance, "ether")

        return value

    def get_block(self, block_number):
        return self.web3.eth.get_block(block_number)

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

    def set_connection(self):

        if self.chain == "eth" or self.chain == "ethereum":
            RPC_URL = config("INFURA_RPC_URL")
            connection = Web3(Web3.HTTPProvider(RPC_URL))

        elif self.chain == "bsc":
            # RPC_URL = "wss://bsc-ws-node.nariox.org:443"
            RPC_URL = "https://bsc-dataseed.binance.org/"

            connection = Web3(Web3.HTTPProvider(
                RPC_URL,
            ))

        else:
            raise ValueError("Chain must be eth or bsc")

        return connection

    def transaction_data(self, transaction_hash):
        receipt = self.get_transaction_receipt(transaction_hash)
        if receipt:
            # receipt = receipt["logs"][0]
            # from_address = self.convert_to_checksum_address(receipt["topics"][1])
            # to_address = self.convert_to_checksum_address(receipt["topics"][2])
            # value = self.convert_from_hex(receipt["data"])
            # print(value)
            # token_address = receipt["address"]
            # block = receipt["blockNumber"]
            # timestamp = datetime.fromtimestamp(self.get_block(block)["timestamp"])

            return receipt
        else:
            return None









