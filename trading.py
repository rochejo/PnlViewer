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


class TradeInventory:
    def __init__(self, lifo=False):
        self.trades = []
        self._idx = -1 if lifo else 0

    def add_trade(self, trade):
        """
        Add trade to existing inventory and returns realized P&L

        Parameters
        ----------
        trade : Trade object

        Returns
        -------
        float

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
        pnl = trade.quantity * (trade.price - t.price) * (1 if t.way == 'Buy' else -1)
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
        float

        """
        return sum([(mark_price - t.price) * t.quantity * (1 if t.way == 'Buy' else -1) for t in self.trades])


class PnlCalculator:
    """
    Parameters
    ----------
    trades_inventory: class to handle trades inventory

    """
    def __init__(self, trades_inventory):
        self.inventory = trades_inventory

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
        df = pd.DataFrame(index=trades.Date.unique(), columns=['Total', 'Realized', 'Unrealized'])
        df.index.name = 'Date'
        df = df.fillna(0)
        positions =  {}

        for grp in trades.groupby(['Date', 'Ticker']):
            date = grp[0][0]
            ticker = grp[0][1]
            if ticker not in positions:
                positions[ticker] = self.inventory()
            pos = positions[ticker]

            real_pnl = 0
            for _, row in grp[1].iterrows():
                trade = Trade(row.Date, row.Ticker, row.Way, row.Quantity, row.Price)
                real_pnl += pos.add_trade(trade)

            unreal_pnl = 0
            if len(pos.trades) > 0:
                close_price = prices.get(date, ticker)
                unreal_pnl = pos.unrealized_pnl(close_price)

            df.at[date, 'Realized'] += real_pnl
            df.at[date, 'Unrealized'] += unreal_pnl

        df['Total'] = df['Realized'] + df['Unrealized']

        return df
