
from algorithms.token_dataset_algos import percent_difference_from_dataset
from django.test import TestCase


class TestCoinPicker(TestCase):
    def setUp(self):
        pass

    def test_get_percent_change_from_dataset(self):
        test_data = [10, 25, 25, 20, 40, 24, 21, 28, 40,
                     60, 75, 60, 66, 79, 101, 200, 210, 220, 310,
                     550, 1050, 1060, 1225, 1310, 2800, 2950, 7560, 7560, 13000]

        result = percent_difference_from_dataset(test_data)

        # Must always be the same size as original dataset
        self.assertEqual(len(test_data), len(result))
        self.assertEqual(result[0][0], 150.)
        self.assertEqual(result[14][0], 98.01980198019802)
        self.assertAlmostEqual(result[3][1], 20)
        # Last day should have all 0s
        self.assertEqual(result[-1], (0, 0, 0))
        # No 6th day should be 0
        self.assertEqual(result[-2][1], 0)
        # No 7th day should be 0
        self.assertEqual(result[-7][2], 0)
