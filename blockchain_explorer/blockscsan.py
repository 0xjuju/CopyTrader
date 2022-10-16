
from decimal import Decimal

from decouple import config
import requests


class Blockscan:
    def __init__(self, chain):
        self.API_KEY = config("ETHERSCAN_API_KEY")

        self.BASE_URL, self.API_KEY = self.chain_map(chain)

    @staticmethod
    def chain_map(chain):
        """
        :param chain: blockchain standard
        :return: (API URL of chain, API KEY)
        """
        chain_data = {
            "ethereum": ("https://api.etherscan.io/api", config("ETHERSCAN_API_KEY"), ),
            "bsc": ("https://api.bscscan.com/api", config("BSC_API_KEY"),),
            "polygon": ("https://api.polygonscan.com/api", config("POLYGONSCAN_API_KEY"), ),
        }
        return chain_data[chain][0], chain_data[chain][1]

    @staticmethod
    def convert_balance_to_eth(*, balance, decimals: int) -> Decimal:
        balance = Decimal(balance)
        return Decimal(balance / (10 ** decimals))

    def request_get_data(self, **kwargs):
        result = requests.get(url=self.BASE_URL, params=kwargs.get("params")).json()
        return result

    def get_block_by_timestamp(self, timestamp):
        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
            "apiKey": self.API_KEY,
        }

        return self.request_get_data(params=params)

    '''
    Get ETH balance of a single address

    arguments:
        address str: A single contract address

    Returns:
        Decimal(123849579385)
    '''

    def get_contract_source_code(self, address):
        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": self.API_KEY,
        }
        return self.request_get_data(params=params)

    def get_eth_balance(self, address: str) -> dict:
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": self.API_KEY,
        }
        return self.request_get_data(params=params)

    '''
    Get ETH balances for multiple wallets, up to 20 

    arguments:
        address_list list: list of contract addresses. Maximum size of 20

    Returns: 
        [{'account': '0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1', 'balance': '12299909866525872'},
         {'account': '0xFea856912F20bc4f7C877C52d60a2cdC797C6Ef8', 'balance': '27103718989226791'}]}
    '''
    def get_multi_eth_balances(self, address_list: list) -> dict:
        if len(address_list) > 20:
            raise ValueError(f"List cannot be greater than 20. {len(address_list)} is invalid")
        address_list = ",".join(address_list)
        params = {
            "module": "account",
            "action": "balancemulti",
            "address": address_list,
            "tag": "latest",
            "apikey": self.API_KEY,
        }

        return self.request_get_data(params=params)

    '''
    transactions between blocks for a given wallet address.
    Max: 10,000 results
    arguments:
        address str: wallet address 
    Returns:
        {'status': '1', 'message': 'OK', 'result': [{'blockNumber': '12908520', 'timeStamp': '1627395235',
         'hash': '0x9087d047c5b6538fd345277fdcbeeea245217e851ffa7887e367d4f75a767682', 'nonce': '38', 
         'blockHash': '0x872c68b1181669825e0c19b534383c47f59cbdf8b8f797bc3a4eacf3c59a8e41', 'transactionIndex': '54', 
         'from': '0xc05189824bf36f2ad9d0f64a222c1c156df28da1', 'to': '0x32a7c02e79c4ea1008dd6564b35f131428673c41', 
         'value': '0', 'gas': '52092', 'gasPrice': '68200000000', 'isError': '0', 'txreceipt_status': '1', 
         'input': '0xa9059cbb00000000000000000000000057a395fbe6b459454dff083b69f2e7641f7eb664
         0000000000000000000000000000000000000000000000018493fba64ef00000', 'contractAddress': '', 
         'cumulativeGasUsed': '5321430', 'gasUsed': '34728', 'confirmations': '34930'}]}
    '''
    def get_normal_transaction_list(self, *, address: str, start_block: int = None, end_block: int = None, sort="asc",
                                    page_number: int = None, offset: int = None) -> dict:
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "sort": sort,
            "startblock": start_block,
            "endblock": end_block,
            "apikey": self.API_KEY,
        }


        if page_number and offset:
            params["page"] = page_number
            params["offset"] = offset

        return self.request_get_data(params=params)
    def get_internal_transaction_list(self, *, address: str, start_block: int = None, end_block: int = None, sort="asc",
                                      page_number: int = None, offset: int = None) -> dict:
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "sort": sort,
            "startblock": start_block,
            "endblock": end_block,
            "page": page_number,
            "offset": offset,
            "apikey": self.API_KEY,
        }
        return self.request_get_data(params=params)

    '''

    Returns:
    {'status': '1', 'message': 'OK', 'result': [{'blockNumber': '12602025', 'timeStamp': '1623264627',
     'hash': '0xfc3f476eb589121f81629505b8eced85d83dfbb2615eee0173f6831963dbeb68',
      'from': '0x7a250d5630b4cf539739df2c5dacb4c659f2488d', 'to': '0xc05189824bf36f2ad9d0f64a222c1c156df28da1',
       'value': '57931493416525872', 'contractAddress': '', 'input': '', 'type': 'call', 'gas': '41881', 'gasUsed': '0',
        'traceId': '4', 'isError': '0', 'errCode': ''}]}
    '''
    def get_token_transfer_events(self, address, start_block: int = None, end_block: int = None, sort: str = "asc",
                                  page_number: int = None, offset: int = None, erc721: int = False,
                                  contract_address: str = None):
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": sort,
            "startblock": start_block,
            "endblock": end_block,
            "page": page_number,
            "offset": offset,
            "contractaddress": contract_address,
            "apikey": self.API_KEY,
        }
        if erc721:
            params["action"] = "tokennfttx"
        return self.request_get_data(params=params)

    def get_internal_transaction_by_hash(self, transaction_hash: str):
        params = {
            "module": "account",
            "action": "txlistinternal",
            "txhas": transaction_hash,
            "apikey": self.API_KEY,
        }
        return self.request_get_data(params=params)


















