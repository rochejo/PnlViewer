import unittest
from datetime import datetime
import charts
from bokeh.plotting.figure import Figure


class ChartsTests(unittest.TestCase):

    def test_pnl_plot(self):
        data = {
            'Date': [datetime(2020, 3, 25), datetime(2020, 3, 26)],
            'Total': [100, 120],
            'Realized': [80, -70],
            'Unrealized': [-20, 50]
        }
        p = charts.pnl_plot(data)

        self.assertIsInstance(p, Figure)
        # Additional checks can be added: max/min values, number of lines...
