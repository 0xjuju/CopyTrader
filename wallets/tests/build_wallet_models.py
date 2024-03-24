
from datetime import datetime

from wallets.models import *


class Build:

    @staticmethod
    def bots():
        bot_list = ("0x4Cb18386e5d1F34dC6EEA834bf3534A970a3f8e7", "0x0000008CF69d25162321FEd9f6789f2A5caDE6bC", )

        uploads = list()

        for each in bot_list:
            uploads.append(Bot(address=each))

        Bot.objects.bulk_create(uploads)


    @staticmethod
    def tokens():
        token_list = (
            ("nexo", "0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"),
            ("FRONT", "0xB62652e35a6c13ee1EE0f84dC5d40bad8d815117"),
            ("ethernity", "0xbbc2ae13b23d715c30720f079fcd9b4a74093505"),
            ("dogechain", "0x7B4328c127B85369D9f82ca0503B000D09CF9180"),
            ("test1", "t1", "0xbbc2ae13b23d715c305ige079fcd9b4a74056b5q",),
            ("test2", "t2", "0xqtc2ae13b23d71asd05ige079fcd9b4a74056b5q",),
            ("test3", "t3", "0x56v2ae13b23d71asd05ige079fcd9b4a74056lk9",),
            ("test4", "t4", "0xqwerty13b23d71asd05ige079fcd9b4a74056ghg5",)
        )

        upload = list()

        for each in token_list:
            upload.append(
                Token(name=each[0], address=each[1])
            )

        Token.objects.bulk_create(upload)

    @staticmethod
    def wallet_filter():
        n = WalletFilter.objects.create(
            top_percent=1,
            min_wallets=5,
            max_wallets=50,
            min_token_wins=2
        )
        n.save()

    @staticmethod
    def wallets():
        tokens = Token.objects.all()
        uploads = [
            Wallet(address="0xa72782657dd132ceec83344488c5a25e2fb2a083"),
            Wallet(address="0xefwjoief3oi45jfoifjf34ijfrfjf34oidfjoiqj"),
            Wallet(address="0x1r3oijfoijgbsraiaiaaaifjerr5oggojf3rjrf3"),
        ]

        Wallet.objects.bulk_create(uploads)

        w = Wallet.objects.first()
        w.token.add(tokens.get(address="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"))
        w.token.add(tokens.get(name="test1"))

        w2 = Wallet.objects.last()
        w2.token.add(tokens.get(name='test1'))
        w2.token.add(tokens.get(name='test2'))
        w2.token.add(tokens.get(name='test3'))

    @staticmethod
    def transactions():
        uploads = [
            Transaction(
                transaction_hash="0xb57bc5b82f09cdde4271f2513805276f51b587e49cba3902d8ec47a3661f4d1d",
                token_in="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206",
                wallet=Wallet.objects.get(address="0xa72782657dd132ceec83344488c5a25e2fb2a083"),
                amount="5908.71",
                percent=25,
                timestamp=datetime(year=2022, month=9, day=5, hour=7, minute=42)
            ),

            Transaction(
                transaction_hash="0x39f3egvj54959jvjf3w34ffw9fj4q309fjw049fjg5e409j9lckmccww8",
                token_in="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206",
                wallet=Wallet.objects.get(address="0xa72782657dd132ceec83344488c5a25e2fb2a083"),
                amount="6400",
                percent=25,
                timestamp=datetime(year=2022, month=10, day=1, hour=7, minute=42)
            ),

            Transaction(
                transaction_hash="0x44ijcvivrjevoirajqr43900d328jq4fj8fj34f88fj89fjv89jr389gqf38f44",
                token_in="0x",
                wallet=Wallet.objects.get(address="0xefwjoief3oi45jfoifjf34ijfrfjf34oidfjoiqj"),
                amount="5908.71",
                percent=25,
                timestamp=datetime(year=2022, month=6, day=22, hour=5, minute=42)
            ),

            Transaction(
                transaction_hash="0xcvnoewicrje9843rh4873echnre3hf5783qfho387fh37w8fhiw384f78h78q3",
                token_in="0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206",
                wallet=Wallet.objects.get(address="0x1r3oijfoijgbsraiaiaaaifjerr5oggojf3rjrf3"),
                amount="5908.71",
                percent=25,
                timestamp=datetime(year=2022, month=8, day=4, hour=7, minute=42)
            )
        ]

        Transaction.objects.bulk_create(uploads)






