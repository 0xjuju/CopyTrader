
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


