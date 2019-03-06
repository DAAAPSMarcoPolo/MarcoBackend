from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from marco_polo.models import Universe, StockInUniverse
from marco_polo.serializers import UniverseSerializer, StockInUniverseSerializer
from knox.auth import TokenAuthentication


class UniverseAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """ Create a new stock universe """
        try:
            user = request.user
            universe_name = request.data["name"]
            universe = Universe.objects.create(user=user, name=universe_name)
            universe_id = universe.id
            universe.save()
            print('created new universe')
        except Exception as e:
            print(e)
            return Response("Could not create new universe", status=status.HTTP_400_BAD_REQUEST)

        stocks = []
        for symbol in request.data["universe"]:
            print(symbol)
            data = {'symbol': symbol,
                    'universe_id': universe_id}
            stock = StockInUniverse.objects.create(symbol=symbol, universe_id=universe_id)
            stocks.append(stock)

        [stock.save() for stock in stocks]
        stocks = [stock.symbol for stock in stocks]
        universe = Universe.objects.get(id=universe_id)
        result_universe = UniverseSerializer(universe, context=self.get_serializer_context()).data
        result_universe['stocks'] = stocks

        return Response(result_universe, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Get a stock universe """
        # TODO
        return Response(request.data, status=status.HTTP_200_OK)