
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
def wallet_hook(request):
    print(request.body)

    return HttpResponse(200)

