from strategy_template import Strategy
import pickle
import talib as ta


class MyStrategy(Strategy):
    portfolio_size = 5

    def __init__(self):
        super().__init__()

    # Visit for technical indicator documentation: http://mrjbq7.github.io/ta-lib/funcs.html
    def add_tech_ind(self, price_map):
        new_price_map = {}

        for symbol in price_map:
            symbol_data = price_map[symbol]
            symbol_data['ema_50'] = ta.EMA(symbol_data['close'], timeperiod=50)
            symbol_data['ema_open_pct_diff'] = (symbol_data['ema_50'] - symbol_data['open']) / symbol_data['open']
            new_price_map[symbol] = symbol_data

        return new_price_map

    def rank_stocks(self, daily_row):
        sorted_daily_data = daily_row.sort_values('ema_open_pct_diff', ascending=False)
        return sorted_daily_data

    def stocks_to_buy(self, portfolio, daily_row):
        # Return an array of tuples with symbol and buy price

        ''' Retrieve the top five stocks with the largest pct change between its open price and 50 day EMA '''
        sorted_daily_data = self.rank_stocks(daily_row)
        symbols = sorted_daily_data.head(5).index

        buy_orders = []
        for symbol in symbols:
            ''' The buy price is the open price because this algo checks to buy in the morning '''
            if symbol not in portfolio:
                order_tup = (symbol, sorted_daily_data.loc[symbol, 'open'])
                buy_orders.append(order_tup)

        return buy_orders

    def stocks_to_sell(self, portfolio, daily_row):
        # Return an array of tuples with symbol and sell price
        sorted_daily_data = self.rank_stocks(daily_row)
        buy_symbols = sorted_daily_data.head(5).index

        sell_orders = []
        for symbol in portfolio:
            if symbol not in buy_symbols:
                order_tup = (symbol, sorted_daily_data.loc[symbol, 'open'])
                sell_orders.append(order_tup)

        return sell_orders


if __name__ == '__main__':
    test = MyStrategy()
    output = open('mean_reversion.pkl', 'wb')
    pickle.dump(test, output)
    output.close()
