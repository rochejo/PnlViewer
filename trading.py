from os.path import join, dirname
import numpy as np
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
        df.Date = pd.to_datetime(df.Date)
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
    Represents a trade
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

    def __eq__(self, other):
        return self.date == other.date and self.ticker == other.ticker and self.way == other.way \
               and self.quantity == other.quantity and self.price == other.price

    def __str__(self):
        return f"{self.way} {self.quantity} '{self.ticker}' @{self.price} ({self.date:%Y-%m-%d})"


class TradePositionFIFO:
    def __init__(self):
        self.trades = []
        self._idx = 0

    def has_position(self):
        return len(self.trades) > 0

    def add_trade(self, trade):
        """
        Add trade to existing position and returns realized P&L

        Parameters
        ----------
        trade : Trade object

        Returns
        -------
        float, realized P&L

        """

        t = None if len(self.trades) == 0 else self.trades[self._idx]

        # No existing position or same way --> trade is added to position
        if t is None or t.way == trade.way:
            self.trades.append(trade)
            return 0

        # Opposite way and qty is lower than existing trade --> qty of existing trade is adjusted
        if trade.quantity < t.quantity:
            t.quantity -= trade.quantity
            return trade.quantity * (trade.price - t.price) * (1 if t.way == 'Buy' else -1)

        # Opposite way and qty is higher than existing trade --> existing trade is removed, qty is adjusted
        pnl = t.quantity * (trade.price - t.price) * (1 if t.way == 'Buy' else -1)
        trade.quantity -= t.quantity
        self.trades.pop(self._idx)
        if trade.quantity > 0:
            pnl += self.add_trade(trade)
        return pnl

    def unrealized_pnl(self, mark_price):
        """
        Calculates unrealized P&L for existing inventory against a reference price

        Parameters
        ----------
        mark_price : float, reference price to use, e.g. close price

        Returns
        -------
        float, unrealized P&L

        """
        return sum([(mark_price - t.price) * t.quantity * (1 if t.way == 'Buy' else -1) for t in self.trades])


class TradePositionLIFO(TradePositionFIFO):
    def __init__(self):
        super().__init__()
        self._idx = -1


class PnlCalculator:
    """
    Parameters
    ----------
    trades_position_class: class to handle trades position/inventory and P&L

    """
    def __init__(self, trades_position_class):
        self.trades_position_class = trades_position_class

    def calculate(self, trades, prices):
        """
        Calculate realized, unrealized and total P&L

        Parameters
        ----------
        trades : DataFrame with the following columns: Date, Ticker, Way, Quantity, Price
        prices: HistPriceCollection

        Returns
        -------
        DataFrame with the following columns: Date, Total, Realized, Unrealized
        """

        # Dates from prices and from trades are merged in order to:
        # 1. calculate unrealized P&L for days there is no trade
        # 2. capture missing price for days with trades
        dates = sorted(set().union(*[trades.Date.to_list(), prices.dates]))

        df = pd.DataFrame(
            index=dates,
            columns=['Total', 'Realized', 'Unrealized'],
            dtype=np.float)
        df.index.name = 'Date'

        # Trades are grouped by date and traversed only once to store them into a dict
        # Assumption: trades are sorted for a given date (trade time is not available)
        trades_by_date = {}
        for g in trades.groupby(['Date']):
            trades_by_date[g[0]] = [Trade(t.Date, t.Ticker, t.Way, t.Quantity, t.Price) for t in g[1].itertuples()]

        pos = {ticker: self.trades_position_class() for ticker in trades.Ticker}

        real_pnl = 0

        for date in dates:

            # Calculate realized P&L by adding trades to current position
            if date in trades_by_date:
                for trade in trades_by_date[date]:
                    real_pnl += pos[trade.ticker].add_trade(trade)

            # Calculate unrealized P&L using outstanding position and close price
            unreal_pnl = sum([pos[ticker].unrealized_pnl(prices.get(date, ticker)) for ticker in pos.keys()])

            df.at[date, 'Realized'] = real_pnl
            df.at[date, 'Unrealized'] = unreal_pnl

        df.Total = df.Realized + df.Unrealized

        return df
