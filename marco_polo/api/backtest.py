from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.backtesting.backtest import Backtest as BT, BTStats
from marco_polo.models import Universe, Backtest, Strategy, UsedUniverse, Stock, User, BacktestTrade, BacktestVote, AlpacaAPIKeys, BacktestGraph
from marco_polo.serializers import UniverseSerializer, UsedUniverseSerializer, BacktestSerializer, BacktestTradeSerializer
import threading
from django.conf import settings
from twilio.rest import Client
from pathlib import Path
import locale
from babel.numbers import format_currency


class BacktestAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        keys = AlpacaAPIKeys.objects.get(id=1)
        universe = Universe.objects.get(id=data['universe'])
        strategy = Strategy.objects.get(id=data['strategy'])

        try:
            user = request.user
            used_universe_name = universe.name
            used_universe = UsedUniverse.objects.create(
                user=user, name=used_universe_name)
            used_universe_id = used_universe.id
            used_universe.save()
            print("created UsedUniverse")
        except Exception as e:
            print(e)
            return Response("Could not create new universe", status=status.HTTP_400_BAD_REQUEST)

        stock_list = UniverseSerializer(
            universe, context=self.get_serializer_context()).data['stocks']

        t = threading.Thread(target=self.add_stocks,
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
            'sharpe': -1,
            'successful': True
        }
        new_backtest_object = Backtest(**bt)
        new_backtest_object.save()
        users = User.objects.filter(is_active=True)
        for u in users:
            BacktestVote.objects.create(
                user=u, backtest=new_backtest_object)
        universe = UniverseSerializer(
            universe, context=self.get_serializer_context()).data
        universe = universe['stocks']
        data['universe'] = universe
        data['strategy'] = Path(strategy.strategy_file.path).stem
        data['keys'] = keys
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

    def backtest_helper(self, user, bt_id, strategy_name, backtest):
        result = backtest.run()
        while backtest.running:
            pass

        bt = Backtest.objects.get(id=bt_id)
        client = Client(settings.TWILIO_ACC_SID,
                        settings.TWILIO_AUTH_TOKEN)

        if result[0]:
            stats = BTStats(backtest).summary
            bt.end_cash = stats['end_funds']
            bt.sharpe = stats['sharpe']
            bt.complete = True
            print('bt is now complete')
            locale.setlocale(locale.LC_ALL, '')
            cash = format_currency(backtest.initial_funds, 'USD', locale='en_US')
            body = "Your backtest on \'" + strategy_name + "\'" + ' between ' + backtest.start_date + ' and ' + \
                   backtest.end_date + ' with ' + cash + ' has been completed.'
            for trade in backtest.trades:
                new_trade = {
                    'backtest': bt,
                    'symbol': trade.symbol,
                    'buy_time': trade.entry_time,
                    'sell_time': trade.exit_time,
                    'buy_price': trade.entry_price,
                    'sell_price': trade.exit_price,
                    'qty': trade.qty
                }
                BacktestTrade.objects.create(**new_trade)
            for performace in backtest.performance:
                new_performace = {
                    'backtest': bt,
                    'date': performace[0],
                    'value': performace[1]
                }
                BacktestGraph.objects.create(**new_performace)

        else:
            bt.successful = False
            bt.complete = False
            body = "Your backtest on \'" + strategy_name + "\'" + ' between ' + backtest.start_date + ' and ' + \
                   backtest.end_date + \
                ' has failed with the following message: \n\n' + str(result[1])

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
            except Exception as e:
                print(e)
                pass
        used_universe.stocks.add(*stocks_to_add)

    def get(self, request, *args, **kwargs):
        try:
            id = self.kwargs["id"]
            backtest = Backtest.objects.get(id=id)
            backtest = BacktestSerializer(
                backtest, context=self.get_serializer_context()).data
            backtest['pct_gain'] = (
                backtest['end_cash'] - backtest['initial_cash']) / backtest['initial_cash']
            print(backtest)
            trades = BacktestTrade.objects.filter(backtest=id).values()
            graph = BacktestGraph.objects.filter(
                backtest=id).order_by('date').values()
            for g in graph:
                g['date'] = g['date'].strftime('%m/%d/%Y')
            for t in trades:
                t['p_l'] = float(t['sell_price'] - t['buy_price']) / float(t['buy_price'])
            backest_details = {
                'backtest': backtest,
                'trades': trades,
                'graph': graph
            }
            return Response(backest_details, status=status.HTTP_200_OK)

        except Exception as e:
            backtests = []
            backtest_list = Backtest.objects.filter(
                successful=True).order_by('-created_at')
            for backtest in backtest_list:
                bt = BacktestSerializer(
                    backtest, context=self.get_serializer_context()).data
                bt['pct_gain'] = (
                    bt['end_cash']-bt['initial_cash']) / bt['initial_cash']
                trades = BacktestTrade.objects.filter(
                    backtest=backtest.id).values()
                graph = BacktestGraph.objects.filter(
                    backtest=backtest.id).order_by('date').values()
                for g in graph:
                    g['date'] = g['date'].strftime('%m/%d/%Y')
                for t in trades:
                    t['p_l'] = float(t['sell_price'] - t['buy_price']) / float(t['buy_price'])
                backest_details = {
                    'backtest': backtest,
                    'trades': trades,
                    'graph': graph
                }
                backtests.append(backest_details)

            return Response(backtests, status=status.HTTP_200_OK)


class BacktestVoteAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # cast vote
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            req = self.request.data
            vote = req['vote']
            bt_id = self.kwargs["id"]
            backtest = Backtest.objects.get(id=bt_id)
            users_voting = BacktestVote.objects.filter(
                backtest=bt_id, user__is_active=True).count()
            if vote == "approve":
                BacktestVote.objects.filter(
                    backtest=bt_id, user=user_id).update(vote=True)
                if backtest.vote_status == "approved":
                    return Response(status=status.HTTP_200_OK)

            elif vote == "deny":
                BacktestVote.objects.filter(
                    backtest=bt_id, user=user_id).update(vote=False)
                if backtest.vote_status == "denied":
                    return Response(status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # check if backtest should be approved for live trading
            approval_votes = BacktestVote.objects.filter(
                backtest=bt_id, user__is_active=True, vote=True).count()
            votes_needed_approval = int(
                users_voting / 2) + int(users_voting % 2)
            vote_pending_approval = False
            if approval_votes >= votes_needed_approval:
                Backtest.objects.filter(id=bt_id).update(
                    vote_status="approved")
                return Response(status=status.HTTP_200_OK)

            # check if backtest should be denied from live trading
            denial_votes = BacktestVote.objects.filter(
                backtest=bt_id, user__is_active=True, vote=False).count()
            votes_needed_denial = int(users_voting / 2)
            vote_pending_denial = False
            if denial_votes >= votes_needed_denial:
                Backtest.objects.filter(id=bt_id).update(
                    vote_status="denied")
                return Response(status=status.HTTP_200_OK)

            Backtest.objects.filter(id=bt_id).update(vote_status="")

            return Response(status=status.HTTP_200_OK)

        # no "id" supplied
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            bt_id = self.kwargs["id"]
            bt = Backtest.objects.get(
                id=bt_id)
            vote_list = BacktestVote.objects.filter(
                backtest=bt_id, user__is_active=True).values('user', 'user__username', 'vote')
            votes = {
                'list': vote_list,
                'status': bt.vote_status
            }
            return Response({'votes': votes}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
