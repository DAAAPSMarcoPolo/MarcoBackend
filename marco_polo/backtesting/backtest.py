from __future__ import division
import math
import statistics
import logging
from datetime import datetime, timedelta
import pandas as pd
import importlib
import pyclbr
import sys
sys.path.append('.../..')
#sys.path.append('../backendStorage/uploads/algos')
#import marco_polo.backendStorage.uploads.algos

from marco_polo.backtesting.market_data import DataFetcher
from marco_polo.backtesting.defaultUniverses.sp500 import Universe
from marco_polo.backtesting.test_data import Test
import sys

class Backtest:

    risk_free_return = .02

    def __init__(self, strategy, initial_funds, universe, start_date, end_date, keys):
        self.strategy = strategy
        self.strategy_name = strategy
        self.initial_funds = float(initial_funds)
        self.current_funds = float(initial_funds)
        self.buying_power = float(initial_funds)
        self.daily_returns = []
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date
        self.keys = keys
        self.open_positions = {}
        self.trades = []
        self.universe_data = {}
        self.performance = []
        self.running = True
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def import_strategy(self):
        sys.path.append("../backendStorage")

        try:
            from os import listdir
            from os.path import isfile, join
            strategy = importlib.import_module('uploads.algos.'+self.strategy)
            module_info = pyclbr.readmodule('uploads.algos.'+self.strategy)

            class_name = None
            for item in module_info.values():
                class_name = item.name

            self.strategy = getattr(strategy, class_name)()
            self.validate_strategy()

        except ImportError as e:
            self.logger.error(e)
            return [False, e]

        return [True, 'imported successfully']

    # Validation Script
    def validate_strategy(self):
        # Check tech ind
        self.logger.info('Validating Strategy')
        error = False
        tester = Test(self.keys)

        price_map = tester.price_map()
        new_price_map = {}
        # Test add_tech_ind()
        try:
            result = self.strategy.add_tech_ind(price_map)
            for key in result:
                test = result[key]
                o = test['open']
                h = test['high']
                l = test['low']
                c = test['close']
                v = test['volume']
                new_price_map = result
        except:
            error = True
            self.logger.error('add_tech_ind() not implemented correctly')
            return [False, 'add_tech_ind() not implemented correctly.']

        if new_price_map:
            daily_data = tester.create_daily_data(new_price_map)
        else:
            self.logger.info('add_tech_ind() must be fixed before the rest of the functions are validated')
            return [False, 'add_tech_ind() must be fixed before the rest of the functions are validated.']
            sys.exit(1)
        # Test rank_stocks()
        try:
            result = self.strategy.rank_stocks(daily_data)

        except Exception as e:
            error = True
            self.logger.error('rank_stocks() not implemented correctly')
            return [False, 'rank_stocks() not implemented correctly.']

        # Test stocks_to_sell()
        try:
            result = self.strategy.stocks_to_sell(['AAPL'], daily_data)
            if type(result) is not list:
                raise Exception
        except:
            error = True
            self.logger.error('stocks_to_sell() not implemented correctly')
            return [False, 'stocks_to_sell() not implemented correctly.']

        # Test stocks_to_buy()
        try:
            result = self.strategy.stocks_to_buy(['AAPL'], daily_data)
            if type(result) is not list:
                raise Exception

        except Exception as e:
            error = True
            self.logger.error('stocks_to_buy() not implemented correctly')
            return [False, 'stocks_to_buy() not implemented correctly.']

        if error:
            self.logger.info('Strategy does not conform to standards')
            sys.exit(1)

        self.logger.info('Strategy Validated')
        return [True, 'valid']

    def set_historical_data(self):
        self.logger.info('Fetching Data...')
        universe_date = {}
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')

        days = (end - start).days

        if days < 1000:
            universe_data = DataFetcher(self.universe, self.start_date, self.end_date, self.keys).daily_data()
            self.universe_data = universe_data
            self.logger.info('Complete.')
            return [True, 'Successfully fetched data']
        else:
            self.logger.error('Start and end date must be less than 1000 days apart')
            return [False, 'Start and end date must be less than 1000 days apart.']

    def buy(self, symbol, entry_price, entry_time, allocated_funds):
        # buy the stock if we do not have it in our portfolio
        if symbol not in self.open_positions:
            if allocated_funds == 0 or entry_price == 0:
                qty = 0
            else:
                qty = math.floor(allocated_funds / entry_price)

            if qty > 0:
                self.open_positions[symbol] = Position(symbol, entry_time, entry_price, qty)
                self.buying_power = self.buying_power - (entry_price * qty)

    def sell(self, symbol, exit_price, exit_time):
        # Close our open position and add it to our completed trades
        self.trades.append(Trade(self.open_positions[symbol], exit_time, exit_price))

        p_l = self.open_positions[symbol].qty * (exit_price - self.open_positions[symbol].entry_price)
        self.performance.append((exit_time, self.current_funds+p_l))
        self.current_funds = self.current_funds + p_l
        self.buying_power = self.buying_power + p_l
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
        #print (curr_date)
        curr_portfolio = []

        for position in self.open_positions:
            symbol = self.open_positions[position].symbol
            curr_portfolio.append(symbol)

        stock_to_sell_tuples = self.strategy.stocks_to_sell(curr_portfolio, daily_data)

        num_avail_pos = self.strategy.portfolio_size - len(stock_to_sell_tuples)
        for tup in stock_to_sell_tuples:
            self.sell(tup[0], tup[1], curr_date)

        daily_pct_made = (self.current_funds - self.initial_funds) / self.initial_funds
        self.daily_returns.append(daily_pct_made)

        allocated_funds = self.buying_power / num_avail_pos

        stock_to_buy_tuples = self.strategy.stocks_to_buy(curr_portfolio, daily_data)
        for tup in stock_to_buy_tuples:
            self.buy(tup[0], tup[1], curr_date, allocated_funds)

    def simulate(self):
        self.logger.info('Running Backtest...')
        daily_dict = self.daily_data_dict()

        day = timedelta(days=1)
        curr_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(self.end_date, '%Y-%m-%d').date() + day
        self.performance.append((curr_date, self.initial_funds))
        while curr_date <= last_date:
            if curr_date in daily_dict:
                daily_data = daily_dict[curr_date]
                self.manage_portfolio(daily_data, curr_date)
            curr_date = curr_date + day

        self.logger.info('Finished Backtest.')
        stats = BTStats(self)
        summary = stats.summary
        print(self.performance[-1])
        print(self.current_funds)
        return [True, summary]

    def run(self):
        result = self.import_strategy()
        if not result[0]:
            self.running = False
            return result

        result = self.set_historical_data()
        if not result[0]:
            self.running = False
            return result

        self.universe_data = self.strategy.add_tech_ind(self.universe_data)
        result = self.simulate()
        self.running = False

        return [True, 'Backtest has ran successfully.']


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
        self.entry_time = position.entry_time
        self.exit_time = exit_time
        self.entry_price = position.entry_price
        self.exit_price = exit_price
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
        self.spy = DataFetcher(['SPY'], bt.start_date, bt.end_date, bt.keys).daily_data()['SPY']

    @property
    def summary(self):
        return {
            'end_funds': self.bt.current_funds,
            'profit': self.realized_profit,
            'pct_return': self.pct_return,
            'sharpe': self.sharpe
        }


    @property
    def realized_profit(self):
        # Total profit made from closed positions
        profit = self.bt.current_funds - self.bt.initial_funds
        profit = round(profit, 2)
        return profit

    @property
    def pct_return(self):
        change = (self.bt.current_funds - self.bt.initial_funds) / self.bt.initial_funds
        change = round(change, 2)
        return change

    @property
    def market_return_rate(self):
        day = timedelta(days=1)
        first_trading_day = datetime.strptime(self.bt.start_date, '%Y-%m-%d').date()
        found = False
        while not found:
            try:
                self.spy.loc[first_trading_day]
                found = True
            except:
                first_trading_day = first_trading_day + day

        sp500_return = (self.spy.iloc[-1].close - self.spy.loc[first_trading_day, 'close']) / self.spy.loc[first_trading_day, 'close']
        return sp500_return

    @property
    def sharpe(self):
        '''
        Usually, any Sharpe ratio greater than 1 is considered acceptable to good by investors.
        A ratio higher than 2 is rated as very good, and a ratio of 3 or higher is considered excellent.
        The basic purpose of the Sharpe ratio is to allow an investor to analyze how much greater a return
        he or she is obtaining in relation to the level of additional risk taken to generate that return.
        sharpe_ratio = (Portfolio Return - Risk Free Rate) / Standard deviation of excess returns
        '''
        diff_return = (self.pct_return - self.market_return_rate)
        s_d = statistics.stdev(self.bt.daily_returns)
        if diff_return == 0 or s_d == 0:
            sharpe = 0.0
        else:
            sharpe = round(diff_return / s_d, 2)
        return sharpe

#
# class PrintColors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#
#
# # Demo Backtests
#
# # Correct Strategy
# class Keys:
#     def __init__(self, key_id, secret_key):
#         self.key_id = key_id
#         self.secret_key = secret_key
# keys = Keys('PK3MIMJUUKM3UT7QCLNA', '/B6IuGjp8JmhCPWkMfILmYbS91i1c4L9p02oTV9e')
# bt = Backtest('mean_reversion', 1000, Universe, '2018-1-1', '2019-2-13', keys=keys)
# bt.run()
# btStats = BTStats(bt)
#time.sleep(.1)
#
# print(PrintColors.OKGREEN)
# print("Initial Funds: ${}".format(round(bt.initial_funds, 2)))
# print("End Funds: ${}".format(round(bt.current_funds, 2)))
# print("Profit: ${}".format(btStats.realized_profit))
# print("% Return: {}%".format(round(btStats.pct_return*100,2)))
# print("Sharpe Ratio: {}".format(btStats.sharpe))
# print(PrintColors.ENDC)
#
# time.sleep(3)
# print("Now Demoing algorithm validation script...")
#
# # Strategy Val Test 1
# bt = Backtest('bad_strategy1', 1000, Universe, '2018-1-1', '2019-2-13')
# bt.run()
#
# # Strategy Val Test 2
# bt = Backtest('bad_strategy2', 1000, Universe, '2018-1-1', '2019-2-13')
# bt.run()
