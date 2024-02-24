import json

from blockchain.alchemy import Blockchain
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from wallets.rank_wallets import get_wallets
from wallets.models import Gem, Wallet


@csrf_exempt
def wallet_hook(request):

    wallets = get_wallets()
    wallet_address_list = wallets.values_list("address", flat=True)
    wallet_address_list = [i.lower() for i in wallet_address_list]

    body = json.loads(request.body)
    chain = body["event"]["network"]
    events = body["event"]["activity"]
    for event in events:
        pass
        # if event["toAddress"].lower() in wallet_address_list:
        #     gem, _ = Gem.objects.get_or_create(name=event["asset"], contract_address=event["toAddress"])
        #     wallet = Wallet.objects.get(address=event["toAddress"])
        #     gem.wallet.add(wallet)
        #     gem.save()

    return HttpResponse(200)

