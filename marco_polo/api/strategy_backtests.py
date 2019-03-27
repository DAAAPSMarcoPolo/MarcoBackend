from rest_framework import generics, permissions
from knox.auth import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Universe, Backtest, Strategy, BacktestTrade
from marco_polo.serializers import BacktestSerializer


class StrategyBacktests(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            print('here')
            backtests = []
            id = self.kwargs["id"]
            strategy = Strategy.objects.get(id=id)
            backtest_list = Backtest.objects.filter(strategy=strategy)
            for backtest in backtest_list:
                bt = BacktestSerializer(backtest, context=self.get_serializer_context()).data
                trades = BacktestTrade.objects.filter(backtest=backtest.id).values()
                backest_details = {
                    'backtest': bt,
                    'trades': trades
                }
                backtests.append(backest_details)

            return Response(backtests, status=status.HTTP_200_OK)

        except Exception as e:
            return Response('No matching strategy', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
