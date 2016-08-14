import unittest

from util import is_empty

class is_empty_Tests(unittest.TestCase):
    def test_with_infinate_generator(self):
        class infinate_gen:
            def __init__(self):
                self.n = 0

            def __iter__(self):
                return self

            def __next__(self):
                result, self.n = self.n, self.n+1
                return result

        self.assertFalse(is_empty(infinate_gen()))

    def test_with_empty_generator(self):
        class empty_gen:
            def __iter__(self):
                return self

            def __next__(self):
                raise StopIteration()

        self.assertTrue(is_empty(empty_gen()))

    def test_with_non_generators(self):
        types = [
            list,
            dict,
            str,
            bytes,
        ]

        map(self.assertTrue, map(is_empty, map(lambda t: t(), types)))

