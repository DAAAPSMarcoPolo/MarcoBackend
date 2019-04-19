from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import AlpacaAPIKeys
from knox.auth import TokenAuthentication
import alpaca_trade_api as tradeapi
from rest_framework import status

class LiveFundsApi(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        try:
            ApiKey = AlpacaAPIKeys.objects.get(id=1)
        except AlpacaAPIKeys.DoesNotExist:
            print("API Key not found")
            return Response("No API key associated with given user", status=status.HTTP_400_BAD_REQUEST)

        amount = self.api = tradeapi.REST(
            key_id=ApiKey.key_id,
            secret_key=ApiKey.secret_key,
            base_url='https://paper-api.alpaca.markets/'
        ).get_account().buying_power

        return Response({'value': amount}, status=status.HTTP_200_OK)