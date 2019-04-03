import alpaca_trade_api as trade_api
import numpy as np
import pandas as pd
import sys
import importlib
import pyclbr
import logging
import datetime
from datetime import datetime, timedelta

from marco_polo.backtesting.market_data import DataFetcher


class live:

    def __init__(self, strategy, universe, operating_funds):
        self.strategy = strategy
        self.strategy_name = strategy
        self.universe = universe
        self.operating_funds = operating_funds
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

    def initial_price_map(self):
        self.logger.info('Fetching Data...')
        now = datetime.datetime.now()
        start = now - timedelta(days=180)
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(now, '%Y-%m-%d')

        price_map = DataFetcher(self.universe, self.start_date, self.end_date).daily_data()
        self.universe_data = universe_data
        self.logger.info('Complete.')
        return [True, 'Successfully fetched data']


    def process_new_data(self):
        pass

    def run(self):
        price_map = self.initial_price_map()


