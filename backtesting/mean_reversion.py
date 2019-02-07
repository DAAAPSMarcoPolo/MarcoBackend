from strategy_template import Strategy
import pickle


class MyStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def buy_condition(self, daily_row):
        return 'buy'

    def sell_condition(self):
        return 'sell'


test = MyStrategy()
output = open('mean_reversion.pkl', 'wb')
pickle.dump(test, output)
output.close()