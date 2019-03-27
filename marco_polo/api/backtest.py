from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.backtesting.backtest import Backtest as BT, BTStats
from marco_polo.models import Universe, Backtest, Strategy, UsedUniverse, Stock, User, BacktestTrade
from marco_polo.serializers import UniverseSerializer, UsedUniverseSerializer, BacktestSerializer, BacktestTradeSerializer
import threading
from django.conf import settings
from twilio.rest import Client
from pathlib import Path


class BacktestAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        universe = Universe.objects.get(id=data['universe'])
        strategy = Strategy.objects.get(id=data['strategy'])

        try:
            user = request.user
            used_universe_name = universe.name
            used_universe = UsedUniverse.objects.create(user=user, name=used_universe_name)
            used_universe_id = used_universe.id
            used_universe.save()
            print("created UsedUniverse")
        except Exception as e:
            print(e)
            return Response("Could not create new universe", status=status.HTTP_400_BAD_REQUEST)

        stock_list = UniverseSerializer(universe, context=self.get_serializer_context()).data['stocks']

        t = threading.Thread(target=self.backtest_helper,
                              args=(used_universe, stock_list))
        t.setDaemon(True)
        t.start()

        used_universe = UsedUniverse.objects.get(id=used_universe_id)
        print('finished adding new stocks')
        bt = {
            'user': request.user,
            'strategy': strategy,
            'universe': used_universe,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'initial_cash': data['initial_funds'],
            'end_cash': data['initial_funds'],
            'sharpe': -1
        }
        new_backtest_object = Backtest(**bt)
        new_backtest_object.save()
        universe = UniverseSerializer(universe, context=self.get_serializer_context()).data
        universe = universe['stocks']
        data['universe'] = universe
        data['strategy'] = Path(strategy.strategy_file.path).stem
        strategy_name = strategy.name
        new_backtest = BT(**data)
        user = User.objects.select_related('profile') \
                .values('username', 'first_name', 'last_name', 'profile__phone_number') \
                .get(username=request.user.username)
        t2 = threading.Thread(target=self.backtest_helper,
                             args=(user, new_backtest_object.id, strategy_name, new_backtest))
        t2.setDaemon(True)
        t2.start()

        return Response('bt is running now!', status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        # TODO
        return Response(request.data, status=status.HTTP_200_OK)

    def backtest_helper(self, user, bt_id, strategy_name, backtest):
        backtest.run()
        while backtest.running:
            pass

        stats = BTStats(backtest).summary
        bt = Backtest.objects.get(id=bt_id)
        bt.end_cash = stats['end_funds']
        bt.sharpe = stats['sharpe']
        bt.complete = True
        print('bt is now complete')
        client = Client(settings.TWILIO_ACC_SID,
                        settings.TWILIO_AUTH_TOKEN)
        body = "Your backtest on \'" + strategy_name + "\'" + ' between ' + backtest.start_date + ' and ' + backtest.end_date + ' has been completed.'

        for trade in backtest.trades:
            new_trade = {
                'backtest': bt,
                'symbol': trade.symbol,
                'buy_time': trade.entry_time,
                'sell_time': trade.exit_time,
                'buy_price': trade.entry_price,
                'sell_price': trade.exit_price,
                'qty': trade.exit_price
            }
            BacktestTrade.objects.create(**new_trade)

        try:
            client.messages.create(
                body=body,
                from_='8475586630',
                to=user['profile__phone_number']
            )
        except Exception as e:
            print("Twilio error:")
            print(e)
        bt.save()

    def add_stocks(self, used_universe, stock_list):
        stocks_to_add = []
        for stock in stock_list:
            try:
                Stock.objects.get(symbol=stock)
                stocks_to_add.append(stock)
            except:
                pass
        used_universe.stocks.add(*stocks_to_add)

    def get(self, request, *args, **kwargs):
        try:
            id = self.kwargs["id"]
            backtest = Backtest.objects.get(id=id)
            backtest = BacktestSerializer(backtest, context=self.get_serializer_context()).data
            trades = BacktestTrade.objects.filter(backtest=id).values()
            backest_details = {
                'backtest': backtest,
                'trades': trades
            }

            return Response(backest_details, status=status.HTTP_200_OK)

        except Exception as e:
            backtests = []
            backtest_list = Backtest.objects.all()
            for backtest in backtest_list:
                bt = BacktestSerializer(backtest, context=self.get_serializer_context()).data
                trades = BacktestTrade.objects.filter(backtest=backtest.id).values()
                backest_details = {
                    'backtest': bt,
                    'trades': trades
                }
                backtests.append(backest_details)

            return Response(backtests, status=status.HTTP_200_OK)

