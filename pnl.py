import pandas as pd
from trading import Trade, PositionManager


class FifoPnlCalculator:

    @staticmethod
    def calculate(trades, prices):
        """
        Calculate realized, unrealized and total P&L using the First-In-First-Out methodology

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
        positions =  PositionManager()

        for grp in trades.groupby(['Date', 'Ticker']):
            date = grp[0][0]
            ticker = grp[0][1]
            real_pnl = 0
            unreal_pnl = 0

            for _, row in grp[1].iterrows():
                trade = Trade(row.Date, row.Ticker, row.Way, row.Quantity, row.Price)
                real_pnl += trade.cashflow()
                positions.add_trade_fifo(trade)

            if positions.has_position(ticker):
                close_price = prices.get(date, ticker)
                unreal_pnl = sum([t.mtm_pnl(close_price) for t in positions.get_trades(ticker)])

            df.at[date, 'Realized'] += real_pnl
            df.at[date, 'Unrealized'] += unreal_pnl

        df['Total'] = df['Realized'] + df['Unrealized']

        return df


class LifoPnlCalculator:

    @staticmethod
    def calculate(trades, prices):
        raise NotImplementedError
