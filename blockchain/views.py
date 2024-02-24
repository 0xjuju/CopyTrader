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

    events = body["event"]["activity"]
    for event in events:
        print(event)
        logs = event["log"]
        data = logs["data"]
        topics = logs["topics"]
        tx_hash = logs["transactionHash"]
        decoded_logs = blockchain.get_event(data, topics, "Any")

        gem, _ = Gem.objects.get_or_create(
            name=event["asset"], contract_address=event["toAddress"], event=decoded_logs.event, transaction_hash=tx_hash
        )
        wallet = Wallet.objects.get(address=event["toAddress"])
        gem.wallet.add(wallet)
        gem.save()

    return HttpResponse(200)

