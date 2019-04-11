import alpaca_trade_api as tradeapi
import sys
import importlib
import pyclbr
import logging
import schedule
from datetime import datetime, timedelta
import time
from marco_polo.models import LiveTradeInstance, LiveTradeInstancePosition, User

from django.conf import settings
from twilio.rest import Client

from marco_polo.backtesting.market_data import DataFetcher


class Live:

    def __init__(self, id, strategy, universe, operating_funds, keys):
        self.id = id
        self.strategy = strategy
        self.strategy_name = strategy
        self.universe = universe
        self.operating_funds = float(operating_funds)
        self.price_map = None
        self.open_price_map = None
        self.open_positions = []
        self.api = tradeapi.REST(key_id='PK3MIMJUUKM3UT7QCLNA',
                                 secret_key='/B6IuGjp8JmhCPWkMfILmYbS91i1c4L9p02oTV9e',
                                 base_url='https://paper-api.alpaca.market')
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def import_strategy(self):
        sys.path.append("../backendStorage")
        print(sys.path)

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

    def sell(self, symbol):
        now = datetime.now()
        position = LiveTradeInstancePosition.objects.filter(id=self.id, open=True, symbol=symbol)[0]
        response = self.api.submit_order(symbol=position.symbol,
                                         qty=position.qty,
                                         side='sell',
                                         type='market',
                                         time_in_force='gtc')
        position.close_date = now
        position.close_price = response.filled_avg_price
        position.open = False
        position.save()

        #update operating funds:
        p_l = position.qty * (position.close_price - position.entry_price)
        self.operating_funds = self.operating_funds + p_l

        users = User.objects.values('username', 'is_active', 'is_staff')
        client = Client(settings.TWILIO_ACC_SID,
                        settings.TWILIO_AUTH_TOKEN)
        body = self.strategy_name + " has sold " + str(position.qty) + " shares of " + symbol + "for a P/L of: " + str(p_l)
        for u in users:
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:")
                print(e)

    def buy(self, symbol, max_funds, qty=None):
        now = datetime.now()
        ask = self.api.last_quote(symbol=symbol).ask

        if qty is None:
            qty = float(max_funds) / float(ask)

        response = None
        try:
            response = self.api.submit_order(symbol=symbol,
                                             qty=qty,
                                             side='buy',
                                             type='market',
                                             time_in_force='gtc')
        except:
            self.buy(symbol, max_funds, qty-1)

        position = LiveTradeInstancePosition.objects.create(live_trade_instance_id=self.id,
                                                            symbol=symbol,
                                                            open_date=response.filled_at,
                                                            open_price=response.filled_avg_price,
                                                            qty=qty,
                                                            open=True)
        equity = response.filled_avg_price * qty
        self.operating_funds = self.operating_funds - equity

        users = User.objects.values('username', 'is_active', 'is_staff')
        client = Client(settings.TWILIO_ACC_SID,
                        settings.TWILIO_AUTH_TOKEN)
        body = self.strategy_name + " has bought " + str(position.qty) + " shares of " + symbol + "for a P/L of: " + str(equity)
        for u in users:
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:")
                print(e)

    def manage_portfolio(self):
        open_positions = LiveTradeInstancePosition.objects.filter(id=self.id, open=True)

        curr_portfolio = []
        for position in open_positions:
            curr_portfolio.append(position.symbol)

        stock_to_sell_tuples = self.strategy.stocks_to_sell(curr_portfolio, self.price_map)

        for tup in stock_to_sell_tuples:
            self.sell(tup[0])

        open_positions = LiveTradeInstancePosition.objects.filter(id=self.id, open=True)
        allocated_funds = self.operating_funds / (self.strategy.portfolio_size - len(open_positions))

        stock_to_buy_tuples = self.strategy.stocks_to_buy(curr_portfolio, self.price_map)
        for tup in stock_to_buy_tuples:
            self.buy(tup[0], tup[1], allocated_funds)

    def trading_day(self):
        clock = self.api.get_clock()
        if clock.is_open:
            return True
        return False

    def run(self):
        live_instance = LiveTradeInstance.objects.get(id=self.id)
        live_instance.live = True
        live_instance.save()

        if self.trading_day():
            self.import_strategy()
            self.init_price_map()

            schedule.every().monday.at("09:30").do(self.manage_portfolio)
            schedule.every().tuesday.at("09:30").do(self.manage_portfolio)
            schedule.every().wednesday.at("09:30").do(self.manage_portfolio)
            schedule.every().thursday.at("09:30").do(self.manage_portfolio)
            schedule.every().friday.at("09:30").do(self.manage_portfolio)

        while True:
            schedule.run_pending()
            time.sleep(5)
