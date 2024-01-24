
from trading_bot.quant import *


class Bot:
    def __init__(self, interval: str):
        self.interval = interval
        pass

    def check_intervals(self):
        intervals = [
            "1min", "5min", "15min", "30min", "1hr", "2hr", "4hr", "6hr", "8hr", "12hr", "24hr",
        ]
        if self.interval not in intervals:
            raise ValueError(f"{self.interval} not an a valid choice. Options are: {intervals}")

    @staticmethod
    def extract_volatile_charts(datasets: list[list], depth: int, variation_percent: float, vol_threshold: int):
        if depth > len(datasets):
            raise IndexError(f"depth {depth} cannot be greater than length of dataset: {len(datasets)}")

        volatile_charts = list()
        for dataset in datasets:
            subset = dataset[0:depth]
            volatility_pattern = get_average_percent_change(subset)
            frequency_of_vol = 0
            for value in volatility_pattern:
                if value >= variation_percent:
                    frequency_of_vol += 1

            if frequency_of_vol >= vol_threshold:
                volatile_charts.append(subset)







