
from datetime import datetime

from wallets.models import (Token, Transaction, Wallet)


class Build:

    @staticmethod
    def tokens():
        token_list = (
            ("Nexo", "0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206",),
            ("DefiChain", "0x8fc8f8269ebca376d046ce292dc7eac40c8d358a",),
            ("Parastate", "0xdc6104b7993e997ca5f08acab7d3ae86e13d20a6",),
        )

        upload = list()

        for each in token_list:
            upload.append(
                Token(name=each[0], address=each[1]),
            )

        Token.objects.bulk_create(upload)

    @staticmethod
    def wallets():
        tokens = Token.objects.all()
        uploads = [
            Wallet(address="0xa72782657dd132ceec83344488c5a25e2fb2a083", token=tokens.objects.get(address="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206")),
        ]

        Wallet.objects.bulk_create(uploads)

    @staticmethod
    def transactions():
        uploads = [
            Transaction(
                transaction_hash="0xb57bc5b82f09cdde4271f2513805276f51b587e49cba3902d8ec47a3661f4d1d",
                token_in="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206",
                wallet=Wallet.objects.get(address="0xa72782657dd132ceec83344488c5a25e2fb2a083"),
                amount="5908.71",
                timestamp=datetime(year=2022, month=9 , day=5, hour=7, minute=42)
            )
        ]






