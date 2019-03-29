from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from marco_polo.models import Universe, Stock
from marco_polo.serializers import UniverseSerializer, Stock
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
            print("created new universe")
        except Exception as e:
            print(e)
            return Response("Could not create new universe", status=status.HTTP_400_BAD_REQUEST)

        stock_list = list(set(request.data["universe"]))
        stocks_to_add = []
        for stock in stock_list:
            try:
                Stock.objects.get(symbol=stock)
                stocks_to_add.append(stock)
            except:
                pass
        universe.stocks.add(*stocks_to_add)
        universe = Universe.objects.get(id=universe_id)
        result_universe = UniverseSerializer(universe, context=self.get_serializer_context()).data

        return Response(result_universe, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Get a stock universe """
        # TODO
        try:
            id = self.kwargs["id"]
            universe = Universe.objects.get(id=id)
            print(universe)
            response = UniverseSerializer(universe, context=self.get_serializer_context()).data
            return Response(response, status=status.HTTP_200_OK)

        except:
            universes = Universe.objects.all()
            response = UniverseSerializer(universes, context=self.get_serializer_context(), many=True).data

            return Response(response, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):

        try:
            id = self.kwargs["id"]
            print(id)
            universe = Universe.objects.get(id=id)
            print(universe)
            stock_list = request.data["universe"]
            #stock_list = list(set(stock_list))
            universe.stocks.clear()
            universe.stocks.add(*stock_list)
            response = UniverseSerializer(universe, context=self.get_serializer_context()).data

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response("No universe with this ID was found", status=status.HTTP_200_OK)
