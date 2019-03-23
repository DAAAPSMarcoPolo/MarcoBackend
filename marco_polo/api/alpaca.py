from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from marco_polo.models import Stock, AlpacaAPIKeys
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