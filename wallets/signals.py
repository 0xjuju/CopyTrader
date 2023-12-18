import asyncio

from blockchain.blockchain_explorer import Explorer
from django.db.models.signals import post_save
from django.dispatch import receiver
# from wallets.models import TargetWallet


# @receiver(post_save, sender=TargetWallet)
def track_wallet(sender, instance, created, **kwargs):
    pass
    # if instance.run_tracker is True:
    #     wallet, contract, abi = instance.address, instance.contract, instance.abi
    #
    #     # def get_or_create_eventloop():
    #     #     try:
    #     #         return asyncio.get_event_loop()
    #     #     except RuntimeError as ex:
    #     #         if "There is no current event loop in thread" in str(ex):
    #     #             loop = asyncio.new_event_loop()
    #     #             asyncio.set_event_loop(loop)
    #     #             return asyncio.get_event_loop()
    #
    #     async def job_monitor():
    #         while True:
    #             print('Check triggered jobs on the cluster')
    #             await asyncio.sleep(2)
    #
    #     loop = asyncio.get_event_loop()
    #     task = loop.create_task(job_monitor())
    #
    #     try:
    #         loop.run_until_complete(task)
    #     except asyncio.CancelledError:
    #         pass





