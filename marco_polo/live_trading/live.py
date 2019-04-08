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
import time

from marco_polo.backtesting.market_data import DataFetcher


class Live:

    def __init__(self, strategy, universe, operating_funds, keys):
        self.strategy = strategy
        self.strategy_name = strategy
        self.universe = universe
        self.operating_funds = float(operating_funds)
        self.price_map = None
        self.open_price_map = None
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
        now = datetime.now()
        start = now - timedelta(days=180)

        start = start.strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')

        price_map = DataFetcher(self.universe, start, end).daily_data()
        self.price_map = price_map
        self.open_price_map = {}
        for symbol in price_map:
            self.open_price_map[symbol] = price_map[symbol]['open'].values

        self.price_map = self.strategy.add_tech_ind(self.price_map)
        print(price_map)

        self.logger.info('Finished Fetching data.')

        return True

    def process_new_data(self):
        for symbol in self.price_map:
            last_quote = self.api.polygon.last_quote(symbol).__dict__['_raw']
            ask = last_quote['askprice']
            #bid = last_quote['bidprice']
            self.open_price_map[symbol].append(ask)
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
        self.import_strategy()
        print(self.strategy)
        pid = os.getpid()
        # Need to store the pid in django here.
        self.trade()

        # schedule.every().monday.at("09:30").do(self.trade)
        # schedule.every().tuesday.at("09:30").do(self.trade)
        # schedule.every().wednesday.at("09:30").do(self.trade)
        # schedule.every().thursday.at("09:30").do(self.trade)
        # schedule.every().friday.at("09:30").do(self.trade)
        #
        # while True:
        #     schedule.run_pending()
        #     time.sleep(30)


if __name__ == '__main__':
    live = Live('mean_reversion.py', ['AAPL'], 1000, None)
    live.run()

