from rest_framework import generics, permissions
from knox.auth import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Universe, Backtest, Strategy, BacktestTrade, BacktestVote
from marco_polo.serializers import BacktestSerializer
from datetime import datetime


class StrategyBacktests(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            print('here')
            backtests = []
            backtest_votes = []
            id = self.kwargs["id"]
            strategy = Strategy.objects.get(id=id)
            backtest_list = Backtest.objects.filter(
                strategy=strategy, successful=True).order_by('-created_at')
            for backtest in backtest_list:
                bt = BacktestSerializer(
                    backtest, context=self.get_serializer_context()).data
                trades = BacktestTrade.objects.filter(
                    backtest=backtest.id).values()
                votes = BacktestVote.objects.filter(
                    backtest=id).values('user', 'vote')
                bt = BacktestSerializer(backtest, context=self.get_serializer_context()).data
                bt['pct_gain'] = (bt['end_cash']-bt['initial_cash']) / bt['initial_cash']
                trades = BacktestTrade.objects.filter(backtest=backtest.id).values()
                backest_details = {
                    'backtest': bt,
                    'trades': trades,
                    'votes': votes
                }

                backtests.append(backest_details)

            return Response(backtests, status=status.HTTP_200_OK)

        except Exception as e:
            return Response('No matching strategy', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
