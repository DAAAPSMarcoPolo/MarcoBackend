from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.backtesting.backtest import Backtest as BT, BTStats
from marco_polo.live_trading import live
from marco_polo.models import Universe, Backtest, Strategy, UsedUniverse, Stock, User, BacktestTrade, BacktestVote
from marco_polo.serializers import UniverseSerializer, UsedUniverseSerializer, BacktestSerializer, \
    BacktestTradeSerializer
import threading
from django.conf import settings
from twilio.rest import Client
from pathlib import Path
import locale


class LiveAPI(generics.GenericAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            live_instance = live.Live('mean_reversion.py', ['AAPL'], 1000, None)
            live_instance.run()

        except Exception as e:
            print(e)

        return Response("Running algo live", status=status.HTTP_200_OK)
