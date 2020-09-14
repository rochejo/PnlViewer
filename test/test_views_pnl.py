import unittest
from datetime import datetime
from views.pnl import pnl_chart
from bokeh.plotting.figure import Figure
import pandas as pd

class ViewsPnlTests(unittest.TestCase):

    def test_pnl_chart(self):
        data = {
            'Date': [datetime(2020, 3, 25), datetime(2020, 3, 26)],
            'Total': [100, 120],
            'Realized': [80, -70],
            'Unrealized': [-20, 50]
        }
        p = pnl_chart(pd.DataFrame(data))

        self.assertIsInstance(p, Figure)
        # Additional checks can be added: max/min values, number of lines...
