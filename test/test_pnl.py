import unittest
from datetime import datetime
import pandas as pd
from pnl import FifoPnlCalculator
from mkt_data import HistPriceCollection


class FifoPnlCalculatorTests(unittest.TestCase):

    def test_calculate(self):
        d1 = datetime(2020, 3, 25)
        d2 = datetime(2020, 3, 26)

        prices = HistPriceCollection()
        prices.add(d1, 'DUMMY', 10)
        prices.add(d2, 'DUMMY', 12)

        data = {
            'Date': [d1, d2, d2],
            'Ticker': ['DUMMY', 'DUMMY', 'DUMMY'],
            'Way': ['Buy', 'Sell', 'Buy'],
            'Quantity': [100, 120, 10],
            'Price': [9.5, 10.5, 11.5],
        }
        trades = pd.DataFrame(data=data)
        calc = FifoPnlCalculator()
        pnl = calc.calculate(trades, prices)

        self.assertEqual(-950, pnl.at[d1, 'Realized'])
        self.assertEqual(50, pnl.at[d1, 'Unrealized'])
        self.assertEqual(-900, pnl.at[d1, 'Total'])

        self.assertEqual(1145, pnl.at[d2, 'Realized'])
        self.assertEqual(-15, pnl.at[d2, 'Unrealized'])
        self.assertEqual(1130, pnl.at[d2, 'Total'])
