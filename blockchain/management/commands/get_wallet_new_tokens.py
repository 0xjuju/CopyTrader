
from blockchain.blockchain_explorer import Explorer
from blockchain.models import Chain, ABI
from coingecko.models import Address
from django.core.management.base import BaseCommand
from wallets.rank_wallets import get_wallets
from wallets.models import Wallet, OwnedToken


class Command(BaseCommand):
    def handle(self, *args, **options):
        wallets = get_wallets()
        wallets = Wallet.objects.all()
        chain_list = Chain.objects.values_list("name", flat=True)
        abi = ABI.objects.first().text
        gecko_tokens = Address.objects.all()

        for chain in chain_list:
            print(chain)
            explorer = Explorer(chain)
            gecko_tokens_filtered = gecko_tokens.filter(chain=chain)
            for wallet in wallets:
                for token in gecko_tokens_filtered:
                    if token.contract:
                        balance = explorer.get_balance_of_token(
                            wallet_address=wallet.address,
                            token_contract_address=token.contract,
                            abi=abi,
                        )

                        if balance and balance > 0:
                            token_obj, created = OwnedToken.objects.get_or_create(
                                name=token.token.name,
                                address=token.contract,
                                owner_wallet=wallet,
                            )

                            # Check if balance is different. If so, update the value and save.
                            # save triggers auto_add for date_added field
                            if balance != token_obj.balance:
                                token.balance = balance

                            if created:
                                token_obj.balance_increase = False
                            else:
                                if balance > 0:
                                    # Token has been bought or transferred in account
                                    token_obj.balance_increase = True
                                else:
                                    token_obj.balance_increase = False

                            token.save()

                            print(chain, token.token.name, balance)









