from datetime import datetime, timedelta

from blockchain.blockscsan import Blockscan
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

        wallets = get_wallets()
        wallets.values_list(flat=True)
        top_wallets = wallets[wallet_filter.min_wallets]

        gecko_client = GeckoClient()

        chain_list = [
            "arbitrum-one",
            "avalanche",
            "polygon-pos",
            "ethereum",
            "binance-smart-chain"
        ]

        excluded_tokens = [
            "USDC", "USDT", "USDD", "Tether", "Ethereum", "BNB"
        ]

        for chain in chain_list:
            blockscan = Blockscan(chain)
            exp = Explorer(chain)
            last_30 = datetime.now() - timedelta(minutes=30)
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
                for tx in logs:
                    data = tx["data"]
                    topics = tx["topics"]
                    abi = ""
                    decoded_log = exp.decode_log(data=data, topics=topics, abi=abi)
                    if decoded_log[0] == "swap":
                        wallet = None
                        if wallet in top_wallets:
                            pass


                    break
            break






