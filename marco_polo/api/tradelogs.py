from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import LiveTradeInstance, LiveTradeInstancePosition
from marco_polo.serializers import LiveTradeInstanceSerializer, LiveTradeInstancePositionerializer
from knox.auth import TokenAuthentication

class TradeLogsAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try: 
            id = self.kwargs["id"]
            position = LiveTradeInstancePosition.objects.filter(id=id).values()
            return Response(position, status=status.HTTP_200_OK) 
        except: 
            positions = LiveTradeInstancePosition.objects.all().values()
            return Response(positions, status=status.HTTP_200_OK)
