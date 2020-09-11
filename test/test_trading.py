import unittest
from datetime import datetime
from trading import Trade, TestTradeLoader, PositionManager


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

    def test_cashflow_buy(self):
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        self.assertEqual(-1000, t.cashflow())

    def test_cashflow_sell(self):
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 100, 10)
        self.assertEqual(1000, t.cashflow())

    def test_mtm_pnl_buy(self):
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        self.assertEqual(200, t.mtm_pnl(12))

    def test_mtm_pnl_sell(self):
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 100, 10)
        self.assertEqual(-200, t.mtm_pnl(12))


class PositionManagerTests(unittest.TestCase):

    def test_get_trades(self):
        pos = PositionManager()
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        pos.add_trade_fifo(t)
        self.assertEqual(t, pos.get_trades('DUMMY')[0])

    def test_get_trades_invalid_ticker(self):
        self.assertIsNone(PositionManager().get_trades('XXX'))

    def test_has_position(self):
        pos = PositionManager()
        t = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        pos.add_trade_fifo(t)
        self.assertTrue(pos.has_position('DUMMY'))

    def test_has_position_invalid_ticker(self):
        self.assertFalse(PositionManager().has_position('XXX'))

    def test_add_trade_same_way(self):
        pos = PositionManager()
        t1 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        t2 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 50, 12)
        pos.add_trade_fifo(t1)
        pos.add_trade_fifo(t2)
        self.assertEqual(2, len(pos.get_trades('DUMMY')))
        self.assertEqual(150, sum([t.quantity for t in pos.get_trades('DUMMY')]))

    def test_add_trade_flat(self):
        pos = PositionManager()
        t1 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        t2 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 100, 12)
        pos.add_trade_fifo(t1)
        pos.add_trade_fifo(t2)
        self.assertFalse(pos.has_position('DUMMY'))

    def test_add_trade_decrease(self):
        pos = PositionManager()
        t1 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        t2 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 20, 12)
        pos.add_trade_fifo(t1)
        pos.add_trade_fifo(t2)
        self.assertEqual(1, len(pos.get_trades('DUMMY')))
        self.assertEqual(Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 80, 10), pos.get_trades('DUMMY')[0])

    def test_add_trade_flip(self):
        pos = PositionManager()
        t1 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Buy', 100, 10)
        t2 = Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 120, 12)
        pos.add_trade_fifo(t1)
        pos.add_trade_fifo(t2)
        self.assertEqual(1, len(pos.get_trades('DUMMY')))
        self.assertEqual(Trade(datetime(2020, 3, 25), 'DUMMY', 'Sell', 20, 12), pos.get_trades('DUMMY')[0])
