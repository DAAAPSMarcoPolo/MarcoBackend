from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Backtest, BacktestTrade
from marco_polo.serializers import BacktestSerializer, BacktestTradeSerializer
from knox.auth import TokenAuthentication


class BacktestAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """ Add an Alpaca key pair """
        # TODO
        return Response(request.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        # TODO
        return Response(request.data, status=status.HTTP_200_OK)