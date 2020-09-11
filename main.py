from pnl import FifoPnlCalculator
from trading import TestTradeLoader
from mkt_data import TestPriceLoader
from charts import pnl_plot
from bokeh.plotting import curdoc

trades = TestTradeLoader().load()
prices = TestPriceLoader().load()

pnl_calc = FifoPnlCalculator()
df = pnl_calc.calculate(trades, prices, cumulative=True)

p = pnl_plot(df)

curdoc().title = 'P&L Viewer'
curdoc().add_root(p)