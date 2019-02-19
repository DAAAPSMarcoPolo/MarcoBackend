import alpaca_trade_api as tradeapi
import concurrent.futures
from datetime import datetime
import pandas as pd


class DataFetcher:
    NY = 'America/New_York'
    api = tradeapi.REST(
        key_id='PK3MIMJUUKM3UT7QCLNA',
        secret_key='/B6IuGjp8JmhCPWkMfILmYbS91i1c4L9p02oTV9e'
    )

    def __init__(self, universe, start_date, end_date):
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date

    def _get_polygon_data(self, max_workers=5):
        # Get the map of DataFrame price data from polygon, in parallel
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        modified_start_data = start - pd.Timedelta('180 days')

        def historic_agg(symbol):
            return self.api.polygon.historic_agg(
                'day', symbol, _from=modified_start_data, to=self.end_date).df.sort_index()

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers) as executor:
            results = {}
            future_to_symbol = {
                executor.submit(
                    historic_agg,
                    symbol): symbol for symbol in self.universe}
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    results[symbol] = future.result()
                except Exception as exc:
                    print('{} generated an exception: {}'.format(symbol, exc))

            keys_to_remove = []
            for symbol in results:
                results[symbol].index = results[symbol].index.date
                if results[symbol].empty:
                    keys_to_remove.append(symbol)
    
            for key in keys_to_remove:
                del results[key]

            return results

    ''' 
        Returns a dictionary of prices where each symbol in the universe represents is a key
        corresponding to a pandas DF for that stocks daily data for the specified time frame.
    '''
    def daily_data(self):
        return self._get_polygon_data(max_workers=5)
