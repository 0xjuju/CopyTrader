import json

from blockchain.models import *


def build_generic_abi():
    with open("generic_abi.json") as f:
        abi = json.load(f)
        abi = ABI.objects.create(
            abi_type="erc_generic",
            text=abi
        )
        abi.save()






