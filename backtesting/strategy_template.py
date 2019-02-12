from abc import ABC, abstractmethod


# Do not remove the Strategy class as it provides a definition for what your strategy should include
class Strategy(ABC):

    @abstractmethod
    def stocks_to_buy(self):
        raise NotImplementedError

    @abstractmethod
    def stocks_to_sell(self):
        raise NotImplementedError
