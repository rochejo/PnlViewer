from os.path import join, dirname
import pandas as pd


class CsvTradeLoader:
    """
    Load trades from csv file

    Parameters
    ----------
    csv_path : string, location of csv file to load

    Returns
    -------
    DataFrame with the following columns: Date, Ticker, Way, Quantity, Price

    """
    def __init__(self, csv_path):
        self.path = csv_path

    def load(self):
        df = pd.read_csv(self.path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df


class TestTradeLoader(CsvTradeLoader):
    """
    Derives csv loader where csv path is hardcoded to use sample/test data

    """
    def __init__(self):
        csv_path = join(dirname(__file__), 'data', 'trades.csv')
        super().__init__(csv_path)


class DbTradeLoader:
    """
    Load trades from database (to be implemented)
    """
    def __init__(self):
        raise NotImplementedError


class Trade:
    """
    Represents a  trades from csv file
    """
    def __init__(self, date, ticker, way, quantity, price):

        self.date = date
        self.ticker = ticker
        if quantity <=0:
            raise ValueError(f"Invalid quantity: '{quantity}, it must be higher than 0")
        self.quantity = abs(quantity)
        if way != 'Buy' and way != 'Sell':
            raise ValueError(f"Invalid trade way: '{way}, expected 'Buy' or 'Sell'")
        self.way = way
        self.price = price

    def cashflow(self):
        if self.way == 'Buy':
            return -self.quantity * self.price
        else:
            return self.quantity * self.price

    def mtm_pnl(self, mkt_price):
        if self.way == 'Buy':
            return (mkt_price - self.price) * self.quantity
        else:
            return (self.price - mkt_price) * self.quantity

    def __eq__(self, other):
        return self.date == other.date and self.ticker == other.ticker and self.way == other.way \
               and self.quantity == other.quantity and self.price == other.price

    def __str__(self):
        return f"{self.way} {self.quantity} '{self.ticker}' @{self.price} ({self.date:%Y-%m-%d})"


class PositionManager:
    def __init__(self):
        self.trades = {}

    def get_trades(self, ticker):
        if ticker in self.trades:
            return self.trades[ticker]
        return None

    def has_position(self, ticker):
        return ticker in self.trades and len(self.trades[ticker]) > 0

    def add_trade_fifo(self, trade):
        if trade.ticker not in self.trades:
            self.trades[trade.ticker] = []
        pos = self.get_trades(trade.ticker)

        # No existing position or new trade is in the same direction --> trade is added to position
        if len(pos) == 0 or trade.way == pos[0].way:
            pos.append(trade)
        # New trade is opposite way and qty is lower than 1st trade --> qty of 1st trade is adjusted
        elif trade.quantity < pos[0].quantity:
            pos[0].quantity -= trade.quantity
        # New trade is opposite way and qty is higher than 1st trade --> 1st trade is removed
        else:
            trade.quantity -= pos[0].quantity
            pos.pop(0)
            if trade.quantity > 0:
                self.add_trade_fifo(trade)
