import unittest
from datetime import datetime
import pandas as pd
from pnl import FifoPnlCalculator
from mkt_data import HistPriceCollection


class FifoPnlCalculatorTests(unittest.TestCase):

    def test_calculate(self):
        prices = HistPriceCollection()
        prices.add(datetime(2020, 3, 25), 'DUMMY', 10)
        prices.add(datetime(2020, 3, 26), 'DUMMY', 12)

        d = {'col1': [1, 2], 'col2': [3, 4]}
        df = pd.DataFrame(data=d)

        trades = pd.DataFrame([datetime])
        calc = FifoPnlCalculator()
        calc.calculate()
