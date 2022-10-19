from functools import lru_cache

from asyc_modules.periodic_functions import end_task
from blockchain_explorer.blockchain_explorer import Explorer
from celery import shared_task
from wallets.models import TargetWallet



@lru_cache(maxsize=None)
@shared_task()
def check_balance():
    """
    Check the balance of a wallet and send sms if the balance changes
    :return: None
    """

    try:
        wallet = TargetWallet.objects.get(name="bloktopia vesting wallet")
        ex = Explorer(chain=wallet.chain)
        balance = ex.get_balance_of_token(wallet_address=wallet.address, token_contract_address=wallet.contract,
                                          abi=wallet.abi)

        if balance != float(wallet.balance):

            end_task(task_name="check_token_balance",
                     message=f"Balance has changed from ${wallet.balance:,.2f} to ${balance:,.2f}\n"
                             f"Link to Wallet: https://polygonscan.com/token/0x229b1b6c23ff8953d663c4cbb519717e323a0a84?a=0x96167d79e03a37d114fedb14bd9deca2a49ea870")
        else:
            print(balance)

    except Exception as e:
        end_task(task_name="check_token_balance",
                 message=f"Unknown Error detected:\n{e}")













