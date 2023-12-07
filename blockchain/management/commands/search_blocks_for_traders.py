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

        gecko_client = GeckoClient()

        chain_list = [
            "ethereum",
            "arbitrum",
            "polygon",
            "bsc",
        ]

        excluded_tokens = [
            "USDC", "USDT", "USDD", "Tether", "Ethereum", "BNB"
        ]

        for chain in chain_list[1:]:
            print(chain)
            blockscan = Blockscan(chain)
            exp = Explorer(chain)

            last_hour = datetime.now() - timedelta(hours=1)
            timestamp = int(last_hour.timestamp())
            latest_block = exp.get_block()["number"]
            start_block = blockscan.get_block_by_timestamp(timestamp)
            max_chunk = 5000

            gecko_tokens = Address.objects.filter(chain=chain) \
                .exclude(token__name__in=excluded_tokens) \
                .exclude(contract="") \
                .values_list("contract", flat=True)

            contract_list = list()

            for each in gecko_tokens:
                # skip contracrt address if it's not compatible for that chain
                try:
                    contract_list.append(exp.convert_to_checksum_address(each))
                except InvalidAddress:
                    pass

            print(len(contract_list))

            logs = exp.get_logs(max_chunk=max_chunk, fromBlock=start_block, toBlock=latest_block, address=contract_list)
            print(len(logs))

            break






