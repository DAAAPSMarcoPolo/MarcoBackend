import pandas as pd
import pickle

from datetime import datetime, timedelta
from marco_polo.backtesting.market_data import DataFetcher


class Test:
    start_date = '2019-2-19'
    end_date = '2019-2-20'
    price_map = DataFetcher(['AAPL', 'BBUY'], start_date, end_date).daily_data()

    day = timedelta(days=1)
    last_date = datetime.strptime(end_date, '%Y-%m-%d').date() + day

    def price_map(self):
        price_map = DataFetcher(['AAPL', 'BBUY'], self.start_date, self.end_date).daily_data()
        return(price_map)

    def create_daily_data(self, price_map):
        data_by_date = {}
        curr_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        while curr_date < self.last_date:
            data_by_date[curr_date] = pd.DataFrame()
            for symbol in price_map.keys():
                symbol_df = price_map[str(symbol)]
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

            curr_date = curr_date + self.day

            daily_data = data_by_date
            test_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()

        return daily_data[test_date]
