from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import AlpacaAPIKeys
from marco_polo.serializers import AlpacaKeysSerializer


class AlpacaKeysAPI(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        """ Add an Alpaca key pair """

        try:
            api_key, created = AlpacaAPIKeys.objects.get_or_create(id=1)
            api_key.key_id = request.data['key_id']
            api_key.secret_key = request.data['secret_key']
            api_key.save()
            print("Successfully updated/created")
        except Exception as e:
            print(e)
            return Response("Could not update/create Alpaca API key", status=status.HTTP_400_BAD_REQUEST)

        return Response(request.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        try:
            ApiKey = AlpacaAPIKeys.objects.get(id=1)
        except AlpacaAPIKeys.DoesNotExist:
            print("API Key not found")
            return Response("No API key associated with given user", status=status.HTTP_400_BAD_REQUEST)

        response = AlpacaKeysSerializer(ApiKey, context=self.get_serializer_context()).data

        return Response(response)