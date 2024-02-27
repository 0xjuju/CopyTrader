
from coingecko.models import GeckoToken, Address

class BuildGeckoModel:

    def build_models(self):
        self.build_tokens()

    @staticmethod
    def build_tokens():
        tokens = [
            GeckoToken(
                name="Manifold Finance",
                symbol="fold",
                token_id="manifold-finance",
                price_change_24hr=50.37627,
                price_chanage_7d=68.84701599664648,
                rank=721
                       ),

        ]

        GeckoToken.objects.bulk_create(tokens)

    def build_coingecko_addresses_for_tokens(self):
        token = GeckoToken.objects.get(name="Manifold Finance")

        adds = [
            Address(
                contract="0xd084944d3c05cd115c09d072b9f44ba3e0e45921",
                decimals=18,
                chain="ethereum",
                token=token,
            )
        ]

        Address.objects.bulk_create(adds)




