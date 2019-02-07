from abc import ABC, abstractmethod


# Do not remove the Strategy class as it provides a definition for what your strategy should include
class Strategy(ABC):

    @abstractmethod
    def buy_condition(self):
        raise NotImplementedError

    @abstractmethod
    def sell_condition(self):
        raise NotImplementedError
