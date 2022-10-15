from functools import lru_cache

from blockchain_explorer.blockchain_explorer import Explorer
from celery import shared_task
from django_celery_beat.models import PeriodicTask
from twilio_sms.twilio_api import Twilio
from wallets.models import TargetWallet


@lru_cache(maxsize=None)
@shared_task()
def check_balance():
    """
    Check the balance of a wallet and send sms if the balance changes
    :return: None
    """

    wallet = TargetWallet.objects.get(name="bloktopia vesting wallet")
    ex = Explorer(chain=wallet.chain)
    balance = ex.get_balance_of_token(wallet_address=wallet.address, token_contract_address=wallet.contract,
                                      abi=wallet.abi)

    if balance != float(wallet.balance):

        # Send sms if balance has changed
        service = Twilio()
        service.send_sms(body=f"Balance has changed from ${wallet.balance:,.2f} to ${balance:,.2f}")

        # Disable task once wallet is changes and SMS is sent
        task = PeriodicTask.objects.get(name="check_token_balance")
        task.enabled = False
        task.save()
    else:
        print(balance)








