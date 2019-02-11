from strategy_template import Strategy
import pickle
import talib as ta


class MyStrategy(Strategy):

    def __init__(self):
        super().__init__()

    # Visit for technical indicator documentation: http://mrjbq7.github.io/ta-lib/funcs.html
    def add_tech_ind(self, price_map):
        new_price_map = {}

        for symbol in price_map:
            symbol_data = price_map[symbol]
            symbol_data['EMA_50'] = ta.EMA(symbol_data['close'], timeperiod=50)
            new_price_map[symbol] = symbol_data

        return new_price_map

    def buy_condition(self, daily_row):
        return 'buy'

    def sell_condition(self):
        return 'sell'

    # Add your own helper functions as needed.


test = MyStrategy()
output = open('mean_reversion.pkl', 'wb')
pickle.dump(test, output)
output.close()