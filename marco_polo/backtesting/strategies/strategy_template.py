from abc import ABC, abstractmethod


# Do not remove the Strategy class as it provides a definition for what your strategy should include
class Strategy(ABC):

    # Default number rof stocks in our portfolio
    portfolio_size = 5

    @abstractmethod
    def add_tech_ind(self, price_map):
        raise NotImplementedError

    @abstractmethod
    def rank_stocks(self, daily_row):
        raise NotImplementedError

    @abstractmethod
    def stocks_to_buy(self, portfolio, daily_row):
        raise NotImplementedError

    @abstractmethod
    def stocks_to_sell(self, portfolio, daily_row):
        raise NotImplementedError
