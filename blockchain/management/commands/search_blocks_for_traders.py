from datetime import datetime, timedelta

from blockchain.blockscsan import Blockscan
from blockchain.models import ABI
from django.core.management.base import BaseCommand
from blockchain.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken
from wallets.rank_wallets import get_wallets
from wallets.models import WalletFilter
from web3.exceptions import InvalidAddress


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallet_filter = WalletFilter.objects.first()
        erc_generic_abi = ABI.objects.first().text

        wallets = get_wallets()
        top_wallets = wallets.values_list(flat=True)
        # top_wallets = wallets[wallet_filter.min_wallets]

        gecko_client = GeckoClient()

        chain_list = [
            "ethereum",
            "arbitrum-one",
            "avalanche",
            "polygon-pos",
            "binance-smart-chain"
        ]

        excluded_tokens = [
            "USDC", "USDT", "USDD", "Tether", "Ethereum", "BNB", "Arbitrum"
        ]

        for chain in chain_list:
            blockscan = Blockscan(chain)
            exp = Explorer(chain)
            last_30 = datetime.now() - timedelta(minutes=10)
            timestamp = int(last_30.timestamp())
            latest_block = exp.get_block()["number"]
            start_block = blockscan.get_block_by_timestamp(timestamp)
            max_chunk = 5000

            gecko_tokens = Address.objects.filter(chain=chain) \
                .exclude(token__name__in=excluded_tokens) \
                .exclude(contract="") \
                .values_list("contract", flat=True)

            contract_list = list()
            for each in gecko_tokens:
                # skip contract address if it's not compatible for that chain
                try:
                    contract_list.append(exp.convert_to_checksum_address(each))
                except InvalidAddress:
                    pass

            print(f"Number of contracts {len(contract_list)}")
            if contract_list:
                logs = exp.get_logs(max_chunk=max_chunk, fromBlock=start_block, toBlock=latest_block, address=contract_list)
                print(len(logs))
                for tx in logs:
                    data = tx["data"]
                    topics = tx["topics"]
                    print([i.hex() for i in topics])
                    tx_hash = tx["transactionHash"]
                    print("Transaction Hash", tx_hash.hex())
                    # print(tx_hash.hex())
                    decoded_log = exp.decode_log(data=data, topics=topics, abi=erc_generic_abi)
                    # print(decoded_log)
                    if decoded_log[0] == "swap" or decoded_log[0] == "Swap":
                        # print(decoded_log)
                        print("Transaction Hash", tx_hash.hex())
                        wallet = decoded_log[1]["from"]

                        if wallet in top_wallets:
                            pass

            break






