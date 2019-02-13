from __future__ import division
import math
import sys
import pickle
import logging
import time
from datetime import datetime, timedelta
import pandas as pd

from market_data import DataFetcher
from sp500 import Universe

# from strategy_template import Strategy
from mean_reversion import MeanReversion

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
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def deserialize_strategy(self, strategy_name):
        try:
            strategy_file = open(strategy_name+'.pkl', 'rb')
            strategy = pickle.load(strategy_file)
            strategy_file.close()
            return strategy
        except FileNotFoundError as e:
            sys.exit(e)


    def set_historical_data(self):
        self.logger.info('Fetching Data...')
        universe_date = {}
        universe_data = DataFetcher(self.universe, self.start_date, self.end_date).daily_data()
        universe_data = self.strategy.add_tech_ind(universe_data)
        self.universe_data = universe_data
        self.logger.info('Complete.')

    def buy(self, symbol, entry_price, entry_time, allocated_funds):
        # buy the stock if we do not have it in our portfolio
        if symbol not in self.open_positions:
            if allocated_funds == 0 or entry_price == 0:
                qty = 0
            else:
                qty = math.floor(allocated_funds / entry_price)

            if (qty > 0):
                self.open_positions[symbol] = Position(symbol, entry_time, entry_price, qty)

    def sell(self, symbol, exit_price, exit_time):
        # Close our open position and add it to our completed trades
        self.trades.append(Trade(self.open_positions[symbol], exit_time, exit_price))

        p_l = self.open_positions[symbol].qty * (exit_price - self.open_positions[symbol].entry_price)
        self.current_funds = self.current_funds + p_l
        del self.open_positions[symbol]

    def daily_data_dict(self):
        day = timedelta(days=1)
        curr_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(self.end_date, '%Y-%m-%d').date() + day

        data_by_date = {}
        while curr_date < last_date:
            data_by_date[curr_date] = pd.DataFrame()
            for symbol in self.universe_data.keys():
                symbol_df = self.universe_data[str(symbol)]
                # Make sure there is data for this day
                if curr_date in symbol_df.index:
                    symbol_data = symbol_df.loc[curr_date]
                    symbol_data.reindex([symbol])
                    symbol_data_dict = symbol_data.to_dict()
                    symbol_data_dict['symbol'] = symbol
                    data_by_date[curr_date] = data_by_date[curr_date].append(symbol_data_dict, ignore_index=True)

            if len(data_by_date[curr_date].index) > 0:
                data_by_date[curr_date] = data_by_date[curr_date].set_index('symbol')
            else:
                del data_by_date[curr_date]

            curr_date = curr_date + day

        return data_by_date

    def manage_portfolio(self, daily_data, curr_date):
        curr_portfolio = []

        for position in self.open_positions:
            curr_portfolio.append(self.open_positions[position].symbol)

        stock_to_sell_tuples = self.strategy.stocks_to_sell(curr_portfolio, daily_data)
        for tup in stock_to_sell_tuples:
            self.sell(tup[0], tup[1], curr_date)

        allocated_funds = self.current_funds / self.strategy.portfolio_size

        stock_to_buy_tuples = self.strategy.stocks_to_buy(curr_portfolio, daily_data)
        for tup in stock_to_buy_tuples:
            self.buy(tup[0], tup[1], curr_date, allocated_funds)

    def simulate(self):
        self.logger.info('Running Backtest...')
        daily_dict = self.daily_data_dict()

        day = timedelta(days=1)
        curr_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(self.end_date, '%Y-%m-%d').date() + day

        while curr_date <= last_date:
            if curr_date in daily_dict:
                daily_data = daily_dict[curr_date]
                self.manage_portfolio(daily_data, curr_date)
            curr_date = curr_date + day

        self.logger.info('Finished Backtest.')

    def run(self):
        self.set_historical_data()
        self.simulate()


class Position:
    def __init__(self, symbol, entry_time, entry_price, qty):
        self.symbol = symbol
        self.entry_time = entry_time
        self.entry_price = float(entry_price)
        self.qty = qty

    @property
    def cost_basis(self):
        return float(self.qty) * self.entry_price


class Trade:
    def __init__(self, position, exit_time, exit_price):
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


class BTStats:
    def __init__(self, bt):
        self.bt = bt

    @property
    def realized_profit(self):
        # Total profit made from closed positions
        profit = self.bt.current_funds - self.bt.initial_funds
        profit = round(profit, 2)
        return profit

    @property
    def pct_return(self):
        change = (self.bt.current_funds - self.bt.initial_funds) / self.bt.initial_funds
        change = round(change*100, 2)
        return change

    @property
    def market_return_rate(self):
        sp500_return = (self.universe_data['SPY'].iloc[-1]["close"] - self.universe_data['SPY'].iloc[0]["close"]) / \
                       (self.universe_data['SPY'].iloc[-1]["close"] - self.universe_data['SPY'].iloc[0]["close"])
        return sp500_return

    @property
    def alpha(self):
        # Alpha = Return – Risk-free rate of return – beta*(market return - Risk-free rate of return)
        alpha = self.pct_return - self.risk_free_return() - self.beta() * (
        self.market_return_rate - self.risk_free_return())
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


class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


bt = Backtest('mean_reversion', 30000, Universe, '2017-1-1', '2017-2-12')
bt.run()
btStats = BTStats(bt)
time.sleep(.1)
print(PrintColors.OKGREEN)
print("Initial Funds: ${}".format(round(bt.initial_funds, 2)))
print("End Funds: ${}".format(round(bt.current_funds, 2)))
print("Profit: ${}".format(btStats.realized_profit))
print("% Return: {}%".format(btStats.pct_return))
print(PrintColors.ENDC)
