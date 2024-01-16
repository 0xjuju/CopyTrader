import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from wallets.rank_wallets import get_wallets
from wallets.models import Gem, Wallet


@csrf_exempt
def wallet_hook(request):

    wallets = get_wallets()
    wallet_address_list = wallets.values_list("address", flat=True)
    wallet_address_list = [i.lower() for i in wallet_address_list] + ["0xbe3f4b43db5eb49d1f48f53443b9abce45da3b79",
                                                                      ]

    body = json.loads(request.body)

    events = body["event"]["activity"]
    for event in events:
        if event["toAddress"].lower() in wallet_address_list:
            gem, _ = Gem.objects.get_or_create(name=event["name"], address=event["address"])
            wallet = Wallet.objects.get(address=event["address"])
            gem.add(wallet)
            gem.save()
    return HttpResponse(200)

