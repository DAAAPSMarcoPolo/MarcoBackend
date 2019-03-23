from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.backtesting.backtest import Backtest, BTStats

class BacktestAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """ Add an Alpaca key pair """
        data = self.request.data
        new_backtest = Backtest(**data.dict())
        new_backtest.run()
        while new_backtest.running:
            pass
        stats = BTStats(new_backtest)

        return Response(stats.summary, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        # TODO
        return Response(request.data, status=status.HTTP_200_OK)
