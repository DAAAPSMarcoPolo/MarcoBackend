import sys
import pickle
import talib
import pandas as pd

from market_data import DataFetcher
# from strategy_template import Strategy
# from mean_reversion import MyStrategy

class Backtest:

    risk_free_return = .02

    def __init__(self, strategy_name, initial_funds, universe, start_date, end_date):
        self.strategy = self.deserialize_strategy(strategy_name)
        self.initial_funds = float(initial_funds)
        self.current_funds = float(initial_funds)
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date
        self.open_positions = {}
        self.trades = []
        self.deserialized_strategy = None
        self.universe_data = {}

    def deserialize_strategy(self, strategy_name):
        try:
            strategy_file = open(strategy_name+'.pkl', 'rb')
            strategy = pickle.load(strategy_file)
            strategy_file.close()
            return strategy
        except FileNotFoundError as e:
            sys.exit(e)


    def set_historical_data(self):
        print('Fetching Data...')
        universe_date = {}
        universe_data = DataFetcher(self.universe, self.start_date, self.end_date).daily_data()
        universe_data = self.strategy.add_tech_ind(universe_data)
        self.universe_data = universe_data

    @property
    def pct_return(self):
        change = (self.current_funds - self.initial_funds) / self.initial_funds
        return change

    @property
    def market_return_rate(self):
        sp500_return = (self.universe_data['SPY'].iloc[-1]["close"] - self.universe_data['SPY'].iloc[0]["close"]) / \
                 (self.universe_data['SPY'].iloc[-1]["close"] - self.universe_data['SPY'].iloc[0]["close"])
        return sp500_return

    @property
    def alpha(self):
        # Alpha = Return – Risk-free rate of return – beta*(market return - Risk-free rate of return)
        alpha = self.pct_return - self.risk_free_return() - self.beta() * (self.market_return_rate - self.risk_free_return())
        return alpha

    @property
    def beta(self):
        # Beta = (Market rate of return - risk free rate) / portfolio rate of return
        beta = (self.market_return_rate() - self.risk_free_return()) / self.pct_return()
        return beta

    @property
    def sharpe(self):
        # Sharpe = (Portfolio Return - Risk Free Rate) / Standard deviation of excess returns
        sharpe = (self.pct_return() - self.risk_free_return()) / 1
        return sharpe

    @property
    def stats_summary(self):
        stats = {
            'pct_change': self.pct_return(),
            'alpha': self.beta(),
            'beta': self.alpha(),
            'sharpe': self.sharpe()
        }
        return stats

    def buy(self, symbol, entry_time, entry_price, pct_of_portfolio):
        # buy the stock if we do not have it in our portfolio
        if symbol not in self.open_positions:
            qty = (self.current_funds*pct_of_portfolio) / entry_price
            self.open_positions[symbol] = Position(symbol, entry_time, entry_price, qty)

    def sell(self, symbol, exit_time, exit_price):
        # Close our open position and add it to our completed trades
        self.trades.apend(Trade(self.open_positions[symbol], exit_time, exit_price))
        del self.open_positions[symbol]

    # TODO: Write the simulation function
    def simulate(self):
        date = self.start_date
        for key in self.universe_data.keys():
            pass

    def run(self):
        self.set_historical_data()
        print(self.universe_data)
        #self.simulate()


class Position:
    def __int__(self, symbol, entry_time, entry_price, qty):
        self.symbol = symbol
        self.entry_time = entry_time
        self.entry_price = float(entry_price)
        self.qty = qty

    @property
    def cost_basis(self):
        return float(self.qty) * self.entry_price


class Trade:
    def __int__(self, position, exit_time, exit_price):
        self.symbol = position.symbol
        self.entry_time = position.entry_price
        self.exit_time = exit_time
        self.entry_price = position.entry_price
        self.exit_price = exit_time
        self.qty = position.qty

    @property
    def trade_length(self):
        return self.exit_time - self.entry_price

    @property
    def pct_made(self):
        return (self.exit_price - self.entry_price) / self.entry_price


bt = Backtest('mean_reversion', 1, ['AAPL', 'SPY'], '2017-2-2', '2018-2-2')
bt.run()