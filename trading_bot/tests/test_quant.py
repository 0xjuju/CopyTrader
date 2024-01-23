
from django.test import TestCase
import numpy as np
from trading_bot.quant import *


class TestQuant(TestCase):
    def setUp(self):
        pass

    def test_calculate_average_percent_change(self):
        dataset = [0.54, 0.32, 0.12, 0.32, 0.31, 0.30, 0.31, 0.22, 0.19, 0.26]
        change = calculate_avg_abs_percentage_change(dataset)

    def test_calculate_oscillation_of_dataset(self):
        dataset = [1.1, 50, 1.1, 1.1, 1.1]
        frequency = calculate_oscillation_score(dataset)
        self.assertAlmostEquals(frequency, 0.0281, places=3)

        dataset = [0.54, 0.32, 0.12, 0.32, 0.31, 0.30, 0.31, 0.22, 0.19, 0.26]
        frequency = calculate_oscillation_score(dataset)

    def test_percent_change_from_dataset(self):
        dataset = [0.25, 0.32, 0.23, 0.22, 0.23, 0.26, 0.33, 0.27, 0.40, 0.32, 0.35]
        pattern = get_average_percent_change(dataset)
        self.assertEqual(pattern[0], 28.0)
        self.assertEqual(pattern[4], 13.04)
        self.assertEqual(pattern[-1], 9.37)





