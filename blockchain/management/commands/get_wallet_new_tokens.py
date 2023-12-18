
from blockchain.blockchain_explorer import Explorer
from blockchain.models import Chain, ABI
from coingecko.models import Address
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets
from wallets.models import Wallet, OwnedToken


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()
        wallets = Wallet.objects.values_list("address", flat=True)
        chain_list = Chain.objects.values_list("name", flat=True)
        abi = ABI.objects.first().text
        gecko_tokens = Address.objects.all()

        for chain in chain_list:
            print(chain)
            explorer = Explorer(chain)
            gecko_tokens_filtered = gecko_tokens.filter(chain=chain)
            for wallet in wallets:
                print(wallet)
                for token in gecko_tokens_filtered:
                    if token.contract:
                        balance = explorer.get_balance_of_token(
                            wallet_address=wallet,
                            token_contract_address=token.contract,
                            abi=abi,
                        )

                        if balance > 0:
                            print(chain, token.token.name, balance)









