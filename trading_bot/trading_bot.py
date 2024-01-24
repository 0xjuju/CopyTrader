
from blockchain.models import Chain
from trading_bot.quant import *


class Bot:
    def __init__(self, chain, interval: str):
        self.interval = interval
        self.chain = chain
        pass

    def arguments_are_valid(self):
        intervals = [
            "1min", "5min", "15min", "30min", "1hr", "2hr", "4hr", "6hr", "8hr", "12hr", "24hr",
        ]
        if self.interval not in intervals:
            raise ValueError(f"{self.interval} not an a valid choice. Options are: {intervals}")

        chains = Chain.objects.all().values_list("name", flat=True)
        if self.chain not in chains:
            raise ValueError(f"Chain not supported {self.chain}. Options are {chains}")

    @staticmethod
    def extract_volatile_charts(datasets: list[list], depth: int, variation_percent: float, vol_threshold: int):

        volatile_charts = list()
        for dataset in datasets:

            if depth > len(dataset):
                raise IndexError(f"depth {depth} cannot be greater than length of dataset: {len(dataset)}")

            subset = dataset[0:depth]
            volatility_pattern = get_average_percent_change(subset)
            frequency_of_vol = 0
            for value in volatility_pattern:
                if value >= variation_percent:
                    frequency_of_vol += 1

            if frequency_of_vol >= vol_threshold:
                volatile_charts.append(subset)

        return volatile_charts







