
from algorithms.basic_tools import flatten_list
from django.test import TestCase


class TestBasicTools(TestCase):
    def setUp(self) -> None:
        pass

    def test_flatten_list(self):
        data = [
            [1, 2], [3, 4], [5, 6], [7, 8]
        ]

        flat_list = flatten_list(data)
        self.assertEqual(flat_list, [1, 2, 3, 4, 5, 6, 7, 8])






