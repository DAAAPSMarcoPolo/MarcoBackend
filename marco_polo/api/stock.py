from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Stock
from marco_polo.serializers import StockSerializer
from knox.auth import TokenAuthentication


class StockAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """ Get a stock universe """
        try:
            input = self.kwargs["input"]
            stocks = Stock.objects.filter(symbol__istartswith=input).values()
            return Response({"stocks": stocks})

        except Exception as e:
            stocks = Stock.objects.all().values()

            return Response({"stocks": stocks})
