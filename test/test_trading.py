import unittest
from datetime import datetime
import pandas as pd
from mkt_data import HistPriceCollection
from trading import Trade, TestTradeLoader, TradeInventoryFIFO, PnlCalculator


class TestTradeLoaderTests(unittest.TestCase):

    def test_load(self):
        df = TestTradeLoader().load()
        for col in ['Date', 'Ticker', 'Way', 'Quantity', 'Price']:
            self.assertTrue(col in df.columns, f"Column '{col}' not found in data")
        self.assertTrue(len(df.values) > 0)


class TradeTests(unittest.TestCase):

    def test_new(self):
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        self.assertIsInstance(t, Trade)

    def test_new_negative_quantity(self):
        try:
            Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', -100, 10)
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised')

    def test_new_invalid_way(self):
        try:
            Trade(datetime(2020, 3, 25), 'DUMMY', 'XXX', 100, 10)
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised')


class TradeInventoryFIFOTests(unittest.TestCase):

    def test_add_trade_buy(self):
        pos = TradeInventoryFIFO()
        pnl = pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10))
        self.assertEqual(0, pnl)
        self.assertEqual(1, len(pos.trades))

    def test_add_trade_buy_sell_flat(self):
        pos = TradeInventoryFIFO()
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10))
        pnl = pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 100, 12))
        self.assertEqual(200, pnl)
        self.assertEqual(0, len(pos.trades))

    def test_add_trade_buy_sell_decrease(self):
        pos = TradeInventoryFIFO()
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 50, 10))
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 50, 11))
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 80, 12))
        self.assertEqual(1, len(pos.trades))
        self.assertEqual(20, sum([t.quantity for t in pos.trades]))

    def test_add_trade_buy_sell_flip(self):
        pos = TradeInventoryFIFO()
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 50, 10))
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 80, 12))
        self.assertEqual(1, len(pos.trades))
        self.assertEqual('Sell', pos.trades[0].way)
        self.assertEqual(30, sum([t.quantity for t in pos.trades]))

    def test_add_trade_unrealized_pnl(self):
        pos = TradeInventoryFIFO()
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10))
        pos.add_trade(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 50, 11))
        self.assertEqual(250, pos.unrealized_pnl(12))


class PnlCalculatorTests(unittest.TestCase):

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
        calc = PnlCalculator(TradeInventoryFIFO)
        pnl = calc.calculate(trades, prices)

        self.assertEqual(0, pnl.at[d1, 'Realized'])
        self.assertEqual(50, pnl.at[d1, 'Unrealized'])
        self.assertEqual(50, pnl.at[d1, 'Total'])

        self.assertEqual(110, pnl.at[d2, 'Realized'])
        self.assertEqual(-15, pnl.at[d2, 'Unrealized'])
        self.assertEqual(95, pnl.at[d2, 'Total'])
