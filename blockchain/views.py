import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from wallets.rank_wallets import get_wallets


@csrf_exempt
def wallet_hook(request):
    wallets = get_wallets()
    wallet_address_list = wallets.values_list("address", flat=True)
    wallet_address_list = [i.lower() for i in wallet_address_list] + ["0xbe3f4b43db5eb49d1f48f53443b9abce45da3b79",
                                                                      "0x7853b3736edba9d7ce681f2a90264307694f97f2"]

    body = json.loads(request.body)

    events = body["event"]["activity"]
    for event in events:
        if event["toAddress"].lower() in wallet_address_list:
            print(event["asset"])

    return HttpResponse(200)

