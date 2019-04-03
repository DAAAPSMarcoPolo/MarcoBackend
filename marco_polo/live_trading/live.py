import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
import sys
import os
import importlib
import pyclbr
import logging
import schedule
from datetime import datetime, timedelta

from marco_polo.backtesting.market_data import DataFetcher


class Live:

    def __init__(self, strategy, universe, operating_funds, keys):
        self.strategy = strategy
        self.strategy_name = strategy
        self.universe = universe
        self.operating_funds = float(operating_funds)
        self.price_map = None
        self.api = tradeapi.REST(key_id='PK3MIMJUUKM3UT7QCLNA',
                                 secret_key='/B6IuGjp8JmhCPWkMfILmYbS91i1c4L9p02oTV9e')
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def import_strategy(self):
        sys.path.append("../backendStorage")

        try:
            from os import listdir
            from os.path import isfile, join
            strategy = importlib.import_module('uploads.algos.' + self.strategy_name)
            module_info = pyclbr.readmodule('uploads.algos.' + self.strategy_name)

            class_name = None
            for item in module_info.values():
                class_name = item.name

            self.strategy = getattr(strategy, class_name)()

        except ImportError as e:
            self.logger.error(e)
            return False

        self.logger.debug('Successfully loaded ' + self.strategy_name)
        return True

    def init_price_map(self):
        self.logger.info('Fetching Data...')
        now = datetime.datetime.now()
        start = now - timedelta(days=180)
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(now, '%Y-%m-%d')

        price_map = DataFetcher(self.universe, self.start_date, self.end_date).daily_data()
        self.price_map = price_map
        self.logger.info('Finished Fetching data.')

        return True

    def calc_indicators(self):
        pass

    def process_new_data(self):
        for symbol in self.price_map:
            self.api.polygon.last_quote(symbol)
            # Calculate new indicators

        # rank here

        return None

    def buy(self):
        # TODO: Buy stock through alpaca here

        # TODO: Store in django

        pass

    def sell(self):
        # TODO: Sell stock through alpaca

        # TODO: Store in django
        pass

    def trade(self):
        self.init_price_map()
        self.process_new_data()

        # Do ranking and check _buy and check_sell here

    def run(self):
        pid = os.getpid()
        print(pid)
        # Need to store the pid in django here.

        schedule.every().monday.at("9:30").do(self.trade())
        schedule.every().tuesday.at("9:30").do(self.trade())
        schedule.every().wednesday.at("9:30").do(self.trade())
        schedule.every().thursday.at("9:30").do(self.trade())
        schedule.every().friday.at("9:30").do(self.trade())


if __name__ == '__main__':
    live = Live('mean_reversion.py', ['AAPL'], 1000, None)
    live.run()

