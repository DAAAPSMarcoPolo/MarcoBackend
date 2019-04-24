from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.models import Strategy, Backtest, LiveTradeInstance, LiveTradeInstancePosition, Universe


class DashboardAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            strats = Strategy.objects.all()
            strategies = []
            for strategy in strats:
                backtest_q = strategy.backtest_set.all()
                backtests = []
                for backtest in backtest_q:
                    live_instances = backtest.livetradeinstance_set.values(
                        'id', 'live', 'buying_power', 'starting_cash')
                    # add to list of backtests
                    backtests.append({
                        'id': backtest.id,
                        'vote_status': backtest.vote_status,
                        'live_instances': live_instances
                    })
                strategies.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'backtests': backtests
                })
            return Response({'strategies': strategies}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
