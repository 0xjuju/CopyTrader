from datetime import datetime, timedelta

from blockchain.blockscsan import Blockscan
from django.core.management.base import BaseCommand
from blockchain.blockchain_explorer import Explorer
from coingecko.coingecko_api import GeckoClient
from coingecko.models import Address, GeckoToken
from wallets.rank_wallets import get_wallets
from wallets.models import WalletFilter


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

        for chain in chain_list:
            blockscan = Blockscan(chain)
            exp = Explorer(chain)

            last_hour = datetime.now() - timedelta(hours=1)
            timestamp = int(last_hour.timestamp())
            latest_block = exp.get_block()["number"]
            start_block = blockscan.get_block_by_timestamp(timestamp)
            max_chunk = 5000
            print(type(start_block))
            print(type(latest_block))

            gecko_tokens = Address.objects.filter(chain=chain).values_list("contract", flat=True)
            gecko_tokens = [exp.convert_to_checksum_address(i) for i in gecko_tokens]

            logs = exp.get_logs(max_chunk=max_chunk, fromBlock=start_block, toBlock=latest_block, address=gecko_tokens)
            print(logs)








