from os.path import join, dirname
import pandas as pd


class CsvPriceLoader:
    """
    Load historical prices from csv file

    Parameters
    ----------
    csv_path : string, location of csv file to load

    Returns
    -------
    HistPriceCollection

    """
    def __init__(self, csv_path):
        self.path = csv_path

    def load(self):
        df = pd.read_csv(self.path)
        df.Date = pd.to_datetime(df.Date)
        h = HistPriceCollection()
        for row in df.itertuples():
            h.add(row.Date, row.Ticker, row.ClosingPrice)
        return h


class TestPriceLoader(CsvPriceLoader):
    """
    Derives csv loader where csv path is hardcoded to use sample/test data

    """
    def __init__(self):
        csv_path = join(dirname(__file__), 'data', 'closing_prices.csv')
        super().__init__(csv_path)


class DbPriceLoader:
    """
    Load historical prices from database (to be implemented)
    """
    def __init__(self):
        raise NotImplementedError


class BbgPriceLoader:
    """
    Load historical prices from Bloomberg (to be implemented)
    """
    def __init__(self):
        raise NotImplementedError


class HistPriceCollection:
    """
    Collection of historical prices stored in nested dictionaries for optimized performance
    """
    def __init__(self):
        self.data = {}

    @property
    def dates(self):
        return self.data.keys()

    def add(self, date, ticker, price):
        if date not in self.data:
            self.data[date] = {}
        self.data[date][ticker] = price

    def get(self, date, ticker):
        if date in self.data and ticker in self.data[date]:
            return self.data[date][ticker]
        raise KeyError(f"No price found for ticker '{ticker}' as of {date}")
