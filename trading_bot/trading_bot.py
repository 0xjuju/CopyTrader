
from blockchain.models import Chain
from trading_bot.quant import *


class Bot:
    def __init__(self, chain, interval: str):
        self.interval = interval
        self.chain = chain

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
    def extract_volatile_charts(dataset: list, depth: int, variation_percent: float, vol_threshold: int):
        """

        :param dataset: price data
        :param depth: how far to look back in price charts
        :param variation_percent: percentage difference of each price to its neighbors
        :param vol_threshold: number of times there's a change in price >= variation_percent for subset to be returned
        :return: volatile subsets
        """

        try:
            subset = dataset[-depth:]
        except IndexError:
            depth = len(dataset)
            subset = dataset[-depth:]

        volatility_pattern = get_average_percent_change(subset)
        frequency_of_vol = 0
        for value in volatility_pattern:
            if value >= variation_percent:
                frequency_of_vol += 1

        if frequency_of_vol >= vol_threshold:
            return subset
        else:
            return []








