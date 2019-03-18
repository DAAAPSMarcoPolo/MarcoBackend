from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from marco_polo.models import Stock, AlpacaAPIKeys
from marco_polo.serializers import UniverseSerializer, StockInUniverseSerializer
from knox.auth import TokenAuthentication
import alpaca_trade_api as tradeapi


class SeedAPI(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        """ Seed the DB with all the stocks tradable on alpaca """

        keys = AlpacaAPIKeys.objects.get(id=1)
        api = tradeapi.REST(
            key_id=keys.key_id,
            secret_key=keys.secret_key
        )

        assets = api.list_assets()
        tradable_assets = [x for x in assets if x.tradable]
        print(len(tradable_assets))
        stocks = []
        for stock in tradable_assets:
            data = {'symbol': stock.symbol,
                    'exchange:': stock.exchange}
            stock = Stock.objects.create(symbol=stock.symbol, exchange=stock.exchange)
            stocks.append(stock)

        [stock.save() for stock in stocks]
        return Response('created', status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Get a stock universe """
        # TODO
        try:
            id = self.kwargs['id']
            universe = Universe.objects.get(id=id)
            print(universe)
            universe_serializer = serializers.serialize('json', [ universe, ])
            return Response(universe_serializer, status=status.HTTP_200_OK)

        except:
            queryset = Universe.objects.prefetch_related('stocks')
            for o in queryset:
                for stock in o.stocks:
                    print(stock)

            return Response({"universes": queryset}, status=status.HTTP_200_OK)
