from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.live_trading import live
from marco_polo.models import LiveTradeInstance, LiveTradeInstancePosition, Backtest, UsedUniverse, Strategy, AlpacaAPIKeys
from marco_polo.serializers import LiveTradeInstanceSerializer, UsedUniverseSerializer
from pathlib import Path
import psutil
from multiprocessing import Process
import threading
import alpaca_trade_api as trade_api
from datetime import datetime


class LiveAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            data = self.request.data
            mode = data['mode']
            if mode == 'start':
                backtest_id = data['backtest']
                backtest = Backtest.objects.get(id=backtest_id)
                if backtest.vote_status != 'approved':
                    return Response({'error': 'Yikes! You tried to start a live instance on a denied/pending backtest...'},
                                    status=status.HTTP_400_BAD_REQUEST)
                funds = data['funds']
                keys = AlpacaAPIKeys.objects.get(id=1)
                strategy = Strategy.objects.get(id=backtest.strategy.id)
                strategy = Path(strategy.strategy_file.path).stem
                universe = UsedUniverse.objects.get(id=backtest.universe.id)
                universe = UsedUniverseSerializer(
                    universe, context=self.get_serializer_context()).data['stocks']
                bt = Backtest.objects.get(id=backtest_id)
                new_live_instance = LiveTradeInstance.objects.create(
                    backtest_id=backtest_id, live=False, starting_cash=funds, buying_power=funds, strategy_id=bt.strategy_id)
                live_instance_id = new_live_instance.id
                bt_id = bt.id
                #live_backtest_instances = LiveTradeInstance.objects.filter(backtest_id=bt_id)
                new_live_instance.strategy_id = bt.strategy_id
                new_live_instance.save()
                live_instance = live.Live(
                    live_instance_id, strategy, universe, funds, keys)
                strategy_islive = Strategy.objects.get(id=backtest.strategy.id)
                strategy_islive.live = True
                strategy_islive.save()
                from django import db
                db.connections.close_all()
                p = Process(target=self.run_live, args=(
                    live_instance,), daemon=True)
                p.start()

                return Response("Starting up a live instance.", status=status.HTTP_200_OK)

            else:
                live_instance_id = data['id']
                live_instance = LiveTradeInstance.objects.get(
                    id=live_instance_id)
                print('here')
                try:
                    live_instance.live = False
                    live_instance.save()
                    backtest = Backtest.objects.get(
                        id=live_instance.backtest.id)
                    strategy = Strategy.objects.get(id=backtest.strategy.id)
                    strategy.live = False
                    strategy.save()
                    try:
                        p = psutil.Process(live_instance.pid)
                        p.terminate()
                    except:
                        print("killed already")
                    print('here')
                    # Terminate live trading instance
                    print('terminating process')
                    print(live_instance.pid)

                    # Close out open positions in thread in case the market is closed.
                    positions = LiveTradeInstancePosition.objects.filter(
                        live_instance=live_instance, open=True)
                    t = threading.Thread(target=self.close_positions(),
                                         args=(positions,))
                    t.setDaemon(True)
                    t.start()

                except Exception as e:
                    Response(e, status=status.HTTP_400_BAD_REQUEST)

                return Response("Successfully shut down live instance.", status=status.HTTP_200_OK)

        except Exception as e:
            print(e)

        return Response("Something went wrong while trying to start/stop a live instance.",
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def run_live(self, live_instance):
        live_instance.run()

    def close_positions(self, positions):
        if len(positions) > 0:
            keys = AlpacaAPIKeys.objects.get(id=1)
            api = trade_api.REST(key_id=keys.key_id,
                                 secret_key=keys.secret_key,
                                 base_url='https://paper-api.alpaca.market')
            for p in positions:
                symbol = p.symbol
                qty = p.qty
                response = api.submit_order(
                    symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')
                now = datetime.now()
                p.close_date = now
                p.close_price = response.filled_avg_price
                p.save()

    def get(self, request, *args, **kwargs):
        keys = AlpacaAPIKeys.objects.get(id=1)
        api = trade_api.REST(
            key_id=keys.key_id,
            secret_key=keys.secret_key,
            base_url = 'https://paper-api.alpaca.markets'
        )
        try:
            id = self.kwargs["id"]
            live_instance = LiveTradeInstance.objects.get(id=id)

            bt_id = Backtest.objects.get(id=live_instance.backtest_id).id
            positions = LiveTradeInstancePosition.objects.filter(
                backtest_id=bt_id, live_trade_instance_id__lte=live_instance.id).order_by('-open_date', '-close_price')
            closed_positions = LiveTradeInstancePosition.objects.filter(
                backtest_id=bt_id, open=False, live_trade_instance_id__lte=live_instance.id)
            open_positions = LiveTradeInstancePosition.objects.filter(
                backtest_id=bt_id, live_trade_instance_id__lte=live_instance.id)
            initvalue = 0
            finalvalue = 0
            for pos in closed_positions:
                initvalue += pos.open_price * pos.qty
                finalvalue += pos.close_price * pos.qty
            for pos in open_positions:
                curr_price = api.polygon.last_quote(symbol=pos.symbol).bidprice
                initvalue += pos.open_price * pos.qty
                finalvalue += curr_price * pos.qty
            if initvalue != 0:
                pct_gain = (finalvalue - initvalue) / initvalue
            else:
                pct_gain = 0

            live_instance = LiveTradeInstanceSerializer(
                live_instance, context=self.get_serializer_context()).data
            positions = positions.values()
            for p in positions:
                if p['close_price'] is not None:
                    p['p_l'] = (p['close_price'] - p['open_price']) / p['open_price']
                else:
                    p['p_l'] = None
            print(live_instance)
            live_instance_details = {
                'live_instance': live_instance,
                'trades': positions,
                'pct_gain': pct_gain
            }
            return Response(live_instance_details, status=status.HTTP_200_OK)
        except:
            print('whoops')
            all_live_instances = []
            live_instances = LiveTradeInstance.objects.filter(live=True)
            for live_instance in live_instances:

                bt_id = Backtest.objects.get(id=live_instance.backtest_id).id
                positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, live_trade_instance_id__lte=live_instance.id).order_by('-open_date',
                                                                                              '-close_price')
                closed_positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, open=False, live_trade_instance_id__lte=live_instance.id)
                open_positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, live_trade_instance_id__lte=live_instance.id)
                initvalue = 0
                finalvalue = 0
                for pos in closed_positions:
                    initvalue += pos.open_price * pos.qty
                    finalvalue += pos.close_price * pos.qty
                for pos in open_positions:
                    initvalue += pos.open_price * pos.qty
                    curr_price = api.polygon.last_quote(symbol=pos.symbol).bidprice
                    finalvalue += curr_price * pos.qty
                if initvalue != 0:
                    pct_gain = (finalvalue - initvalue) / initvalue
                else:
                    pct_gain = 0

                li = LiveTradeInstanceSerializer(
                    live_instance, context=self.get_serializer_context()).data
                positions = positions.values()
                for p in positions:
                    if p['close_price'] is not None:
                        p['p_l'] = (p['close_price'] - p['open_price']) / p['open_price']
                    else:
                        p['p_l'] = None
                live_instance_details = {
                    'live_instance': li,
                    'trades': positions,
                    'pct_gain': pct_gain,
                }
                all_live_instances.append(live_instance_details)
            return Response(all_live_instances, status=status.HTTP_200_OK)


class StrategyLiveInstanceAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        keys = AlpacaAPIKeys.objects.get(id=1)
        api = trade_api.REST(
            key_id=keys.key_id,
            secret_key=keys.secret_key,
            base_url='https://paper-api.alpaca.markets'
        )
        print('here')
        try:
            id = self.kwargs["id"]
            all_live_instances = []
            live_instances = LiveTradeInstance.objects.filter(strategy_id=id)
            for live_instance in live_instances:
                bt = Backtest.objects.get(id=live_instance.backtest_id)
                bt_id = bt.id
                positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, live_trade_instance_id__lte=live_instance.id).order_by('-open_date', '-close_price')
                closed_positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, open=False, live_trade_instance_id__lte=live_instance.id)
                open_positions = LiveTradeInstancePosition.objects.filter(
                    backtest_id=bt_id, open=True, live_trade_instance_id__lte=live_instance.id)
                initvalue = 0
                finalvalue = 0
                for pos in closed_positions:
                    initvalue += pos.open_price * pos.qty
                    finalvalue += pos.close_price * pos.qty
                for pos in open_positions:
                    initvalue += pos.open_price * pos.qty
                    curr_price = api.polygon.last_quote(symbol=pos.symbol).bidprice
                    finalvalue += curr_price * pos.qty
                if initvalue != 0:
                    pct_gain = (finalvalue - initvalue) / initvalue
                else:
                    pct_gain = 0

                li = LiveTradeInstanceSerializer(
                    live_instance, context=self.get_serializer_context()).data
                positions = positions.values()
                for p in positions:
                    if p['close_price'] is not None:
                        p['p_l'] = (p['close_price'] - p['open_price']) / p['open_price']
                    else:
                        p['p_l'] = None
                live_instance_details = {
                    'live_instance': li,
                    'trades': positions,
                    'pct_gain': pct_gain,
                }
                all_live_instances.append(live_instance_details)
            return Response(all_live_instances, status=status.HTTP_200_OK)
        except:
            return Response("Could not get live instances for given strategy", status=status.HTTP_400_BAD_REQUEST)
