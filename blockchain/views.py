import json

from blockchain.alchemy_webhooks import Webhook
from blockchain.alchemy import Blockchain
from blockchain.models import ABI
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from wallets.rank_wallets import get_wallets
from wallets.models import Gem, Wallet


@csrf_exempt
def wallet_hook(request):

    body = json.loads(request.body)
    chain = Webhook().networks[body["event"]["network"]]
    blockchain = Blockchain(chain)
    web_id = body["webhookId"]
    webhook_wallets = Webhook().get_address_list_from_webhook(web_id)["data"]
    events = body["event"]["activity"]
    for event in events:
        to_address = event["toAddress"]

        # Wallets that are in the webhook address and received a token represent the user receiving transactions
        if to_address in webhook_wallets:
            decoded_logs = blockchain.get_event(data, topics, "Any")
            if decoded_logs.event not in ["Mint", "Burn", "Withdraw"]:

                logs = event["log"]
                data = logs["data"]
                topics = logs["topics"]
                tx_hash = logs["transactionHash"]

                gem, _ = Gem.objects.get_or_create(
                    name=event["asset"], event=decoded_logs.event, transaction_hash=tx_hash
                )
                wallet = Wallet.objects.get(address=event["toAddress"])
                gem.wallet.add(wallet)
                gem.save()

    return HttpResponse(200)

