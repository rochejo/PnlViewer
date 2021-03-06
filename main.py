from trading import TestTradeLoader, TradePositionFIFO, PnlCalculator
from mkt_data import TestPriceLoader
from views.pnl import view_pnl

trades_loader = TestTradeLoader()
prices_loader = TestPriceLoader()
calculator = PnlCalculator(TradePositionFIFO)

trades = trades_loader.load()
prices = prices_loader.load()

pnl = calculator.calculate(trades, prices)
view_pnl(pnl)
