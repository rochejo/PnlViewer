import unittest
from views.pnl import pnl_chart
from bokeh.plotting.figure import Figure
import pandas as pd

class ViewsPnlTests(unittest.TestCase):

    def test_pnl_chart(self):
        data = {
            'Total': [100, 120],
            'Realized': [80, -70],
            'Unrealized': [-20, 50]
        }
        df = pd.DataFrame(data, index=[pd.Timestamp(2020, 3, 25), pd.Timestamp(2020, 3, 26)])
        p = pnl_chart(df)

        self.assertIsInstance(p, Figure)
        # Additional checks can be added: max/min values, number of lines...
