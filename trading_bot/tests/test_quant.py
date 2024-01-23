
from django.test import TestCase
import numpy as np
from trading_bot.quant import *


class TestQuant(TestCase):
    def setUp(self):
        pass

    def test_calculate_oscillation_of_dataset(self):
        dataset = [1.1, 50, 1.1, 1.1, 1.1]
        frequency = calculate_oscillation_score(dataset)
        self.assertAlmostEquals(frequency, 0.0281, places=3)




