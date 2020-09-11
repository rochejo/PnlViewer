import unittest
from datetime import datetime
from mkt_data import TestPriceLoader, HistPriceCollection


class TestPriceLoaderTests(unittest.TestCase):

    def test_load(self):
        prices = TestPriceLoader().load()
        self.assertIsInstance(prices, HistPriceCollection)
        self.assertTrue(len(prices.data) > 0)


class HistPriceCollectionTests(unittest.TestCase):

    def test_add_get(self):
        prices = HistPriceCollection()
        prices.add(datetime(2020, 3, 25), 'DUMMY', 10)
        self.assertEqual(10, prices.get(datetime(2020, 3, 25), 'DUMMY'))

    def test_get_invalid_date(self):
        try:
            prices = HistPriceCollection()
            prices.add(datetime(2020, 3, 25), 'DUMMY', 10)
            self.assertEqual(10, prices.get(datetime(1900, 3, 25), 'DUMMY'))
        except KeyError:
            pass
        else:
            self.fail('KeyError not raised')

    def test_get_invalid_ticker(self):
        try:
            prices = HistPriceCollection()
            prices.add(datetime(2020, 3, 25), 'DUMMY', 10)
            self.assertEqual(10, prices.get(datetime(1900, 3, 25), 'XXX'))
        except KeyError:
            pass
        else:
            self.fail('KeyError not raised')
