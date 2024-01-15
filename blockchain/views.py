import json

import decouple
from django.http import JsonResponse
from django.shortcuts import render
import requests


def wallet_hook(request):
    print(request.body)
    webhook = decouple.config("ALCHEMY_API_KEY")

    return JsonResponse(dict())


def handle_webhook(event, payload):
    """Simple webhook handler that prints the event and payload to the console"""
    print('Received the {} event'.format(event))
    print(json.dumps(payload, indent=4))
