import pickle
import talib
import pandas as pd

from market_data import DataFetcher
# from strategy_template import Strategy
# from mean_reversion import MyStrategy

class Backtest:

    risk_free_return = .02

    def __init__(self, strategy, initial_funds, universe, start_date, end_date):
        self.strategy = strategy
        self.initial_funds = float(initial_funds)
        self.current_funds = float(initial_funds)
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date
        self.positions  = {}
        self.orders = []
        self.deserialized_strategy = None
        self.universe_data = {}

    def deserialize_strategy(self):
        strategy_file = open(self.strategy+'.pkl', 'rb')
        strategy = pickle.load(strategy_file)
        strategy_file.close()
        self.deserialized_strategy = strategy

    def set_historical_data(self):
        print('Fetching Data...')
        self.universe_data = DataFetcher(self.universe, self.start_date, self.end_date).run()

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
        if symbol not in self.positions:
            qty = (self.current_funds*pct_of_portfolio) / entry_price
            self.positions[symbol] = Position(entry_time, entry_price, qty)

    def sell(self, symbol, exit_time, exit_price):
        # Close our open position
        self.positions[symbol].exit_time = exit_time
        self.positions[symbol].exit_price = exit_price

    # TODO: Write the simulation function
    def simulate(self):
        date = self.start_date
        for key in self.universe_data.keys():
            pass

    def run(self):
        #self.deserialize_strategy()
        self.set_historical_data()
        print(self.universe_data)
        #self.simulate()


class Position:

    def __int__(self, entry_time, entry_price, qty):
        self.entry_time = entry_time
        self.exit_time = None
        self.entry_price = float(entry_price)
        self.exit_price = None
        self.qty = qty

    @property
    def cost_basis(self):
        return float(self.qty) * self.entry_price

    @property
    def is_open(self):
        if self.exit_time is None:
            return False
        return True

bt = Backtest('mean_reversion', 1, ['AAPL', 'SPY'], '2017-2-2', '2018-2-2')
bt.run()