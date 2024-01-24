
from django.test import TestCase
from trading_bot.trading_bot import Bot


class TestTradingBot(TestCase):
    def setUp(self):
        self.bot1 = Bot("ethereum", "24hr")
        self.datasets = [
            [1.15, 1.25, 1.32, 1.67, 1.69, 1.74, 1.71, 1.68, 1.72, 1.79],
            [0.0025, 0.0033, 0.0027, 0.0034, 0.0032, 0.0033, 0.0033, 0.0031, 0.0039, 0.0031],
            [157, 350, 165, 162, 154, 165, 171, 180, 188, 180],
            [0.10, 0.09, 0.16, 0.18, 0.21, 0.19, 0.20, 0.20, 0.22, 0.24],
            [0.00075, 0.00099, 0.0019, 0.0005, 0.0001, 0.0002, 0.00015, 0.00045, 0.00062, 0.00040]
        ]

    def test_extract_volatile_charts(self):

        volatile_sets = self.bot1.extract_volatile_charts(
            self.datasets, depth=10, variation_percent=15, vol_threshold=5
        )

        self.assertEqual(volatile_sets[0], self.datasets[1])
        self.assertEqual(volatile_sets[1], self.datasets[4])






