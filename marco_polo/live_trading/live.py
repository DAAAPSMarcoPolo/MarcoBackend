import alpaca_trade_api as tradeapi
import sys
import importlib
import pyclbr
import logging
import schedule
from datetime import datetime, timedelta
import time
import os
import pandas as pd
from marco_polo.models import LiveTradeInstance, LiveTradeInstancePosition, User, Backtest
import dateutil

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
        self.buying_power = operating_funds
        self.keys = keys
        self.price_map = None
        self.daily_data = {}
        self.open_price_map = None
        self.open_positions = []
        self.buying = []
        self.selling = []
        self.p_l = 0.0

        self.api = tradeapi.REST(key_id=keys.key_id,
                                 secret_key=keys.secret_key,
                                 base_url='https://paper-api.alpaca.markets')

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

    def init_price_map(self):
        self.logger.info('Fetching Data...')
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        start = now - timedelta(days=180)

        start = start.strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')

        price_map = DataFetcher(self.universe, start, end, self.keys).daily_data()
        self.price_map = price_map
        self.open_price_map = {}
        for symbol in price_map:
            self.open_price_map[symbol] = price_map[symbol]['open'].values

        self.price_map = self.strategy.add_tech_ind(self.price_map)

        self.logger.info('Finished Fetching data.')

        return True

    def daily_data_dict(self):
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        start = (now - timedelta(days=180)).strftime('%Y-%m-%d')

        day = timedelta(days=1)
        curr_date = datetime.strptime(start, '%Y-%m-%d').date()
        last_date = datetime.strptime(today, '%Y-%m-%d').date() + day

        now = datetime.now()
        today = now.strftime('%Y-%m-%d')

        data_by_date = {}
        while curr_date < last_date:
            data_by_date[curr_date] = pd.DataFrame()
            for symbol in self.price_map.keys():
                symbol_df = self.price_map[str(symbol)]
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

            curr_date = curr_date + day

        last_key = sorted(data_by_date.keys())[-1]
        last = data_by_date[last_key]
        not_found = False
        data_by_date[today] = last
        stocks = last.index
        for stock in stocks:
            data_by_date[today].loc[stock, 'open'] = self.api.polygon.last_quote(symbol=stock).askprice
        self.daily_data = data_by_date

    def open_prices(self):
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')

        stocks = self.daily_data[today].index
        for stock in stocks:
            self.daily_data[today].loc[stock, 'open'] = self.api.polygon.last_quote(symbol=stock).askprice

    def sell(self, symbol):
        now = datetime.now()
        instance = LiveTradeInstance.objects.get(id=self.id)
        backtest = Backtest.objects.get(id=instance.backtest_id).id
        try:
            position = LiveTradeInstancePosition.objects.filter(backtest_id=backtest, open=True, symbol=symbol)[0]
            response = self.api.submit_order(symbol=position.symbol,
                                             qty=position.qty,
                                             side='sell',
                                             type='market',
                                             time_in_force='gtc')
            status = response.status
            order = response.id
            while status != 'filled':
                response = self.api.get_order(order_id=order)
                status = response.status
            position.close_date = response.filled_at
            position.close_price = response.filled_avg_price
            position.open = False
            position.save()

            #update operating funds:
            #p_l = int(position.qty) * (float(position.close_price) - float(position.open_price))
            #self.p_l = self.p_l + p_l
            self.operating_funds = self.operating_funds + int(position.qty)*float(position.close_price)
            self.buying_power = self.buying_power + float(position.close_price) * int(position.qty)
            instance.buying_power = self.buying_power
            instance.save()
            self.selling.append(symbol)
        except:
            pass

    def buy(self, symbol, max_funds, qty=None):
        now = datetime.now()
        ask = self.api.polygon.last_quote(symbol=symbol).askprice

        if qty is None:
            qty = int(float(max_funds) / float(ask))

        if qty <= 0:
            return

        response = None
        self.buying.append(symbol)
        print('buying', symbol)
        instance = LiveTradeInstance.objects.get(id=self.id)
        try:
            response = self.api.submit_order(symbol=symbol,
                                             qty=qty,
                                             side='buy',
                                             type='market',
                                             time_in_force='gtc')
            status = response.status
            order = response.id
            while status != 'filled':
                response = self.api.get_order(order_id=order)
                status = response.status
            backtest = Backtest.objects.get(id=instance.backtest_id)
            position = LiveTradeInstancePosition.objects.create(live_trade_instance_id=self.id,
                                                                backtest=backtest,
                                                                symbol=symbol,
                                                                open_date=response.filled_at,
                                                                open_price=float(response.filled_avg_price),
                                                                qty=int(qty),
                                                                open=True)
            equity = float(response.filled_avg_price)*qty
            self.operating_funds = self.operating_funds - equity
            self.buying_power = float(self.buying_power) - (float(response.filled_avg_price))*qty

            instance.buying_power = float(self.buying_power)
            position.save()
            instance.save()
            print('saved')

        except Exception as e :
            print('whoops')
            print(e)
            self.buy(symbol, max_funds, qty-1)
        return

    def manage_portfolio(self):
        users = User.objects.filter(is_active=True).select_related('profile').values('username',
                                                                                     'profile__phone_number')
        client = Client(settings.TWILIO_ACC_SID,
                        settings.TWILIO_AUTH_TOKEN)

        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = self.daily_data[today]
        instance = LiveTradeInstance.objects.filter(id=self.id)[0]
        backtest = Backtest.objects.get(id=instance.backtest_id).id
        open_positions = LiveTradeInstancePosition.objects.filter(backtest_id=backtest, open=True)
        for p in open_positions:
            p.symbol

        curr_portfolio = []
        for position in open_positions:
            curr_portfolio.append(position.symbol)
        stock_to_sell_tuples = self.strategy.stocks_to_sell(curr_portfolio, daily_data)
        for tup in stock_to_sell_tuples:
            self.sell(tup[0])

        stocks = [x[0] for x in stock_to_sell_tuples]
        if len(stocks) > 0:
            body = self.strategy_name + " has sold " + str(stocks)
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
        #instance.pct_change_closed = (self.p_l - instance.starting_cash) / instance.starting_cash
        #instance.save()
        #self.p_l = 0.0
        self.selling = []
        open_positions = LiveTradeInstancePosition.objects.filter(backtest_id=instance.backtest_id, open=True)
        temp = []
        for p in open_positions:
            temp.append(p.symbol)
        open_positions = temp

        allocated_funds = LiveTradeInstance.objects.filter(id=self.id)[0].buying_power


        stock_to_buy_tuples = self.strategy.stocks_to_buy(curr_portfolio, daily_data)
        stocks = [x[0] for x in stock_to_buy_tuples]
        stocks = list(set(stocks) - set(open_positions))
        print(stocks)

        try:
            allocated_funds = allocated_funds / len(stocks)
        except:
            allocated_funds = 0

        print('funds' + str(allocated_funds))


        for stock in stocks:
            self.buy(stock, allocated_funds)

        if len(self.buying) > 0:
            body = self.strategy_name + " has bought " + str(self.buying)
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
            self.buying = []

    def trading_day(self):
        clock = self.api.get_clock()
        if clock.is_open:
            return True
        return False

    def startup(self):
        self.import_strategy()
        self.init_price_map()
        self.daily_data_dict()

    def trade(self):
        if self.trading_day():
            self.open_prices()
            self.manage_portfolio()

    def run(self):
        live_instance = LiveTradeInstance.objects.get(id=self.id)
        live_instance.live = True
        live_instance.pid = os.getpid()
        live_instance.save()

        schedule.every().monday.at("13:00").do(self.startup)
        schedule.every().tuesday.at("13:00").do(self.startup)
        schedule.every().wednesday.at("13:0").do(self.startup)
        schedule.every().thursday.at("13:00").do(self.startup)
        schedule.every().friday.at("13:00").do(self.startup)

        schedule.every().monday.at("13:30").do(self.trade)
        schedule.every().tuesday.at("13:30").do(self.trade)
        schedule.every().wednesday.at("13:30").do(self.trade)
        schedule.every().thursday.at("13:30").do(self.trade)
        schedule.every().friday.at("13:30").do(self.trade)

        while True:
            schedule.run_pending()
            time.sleep(1)
