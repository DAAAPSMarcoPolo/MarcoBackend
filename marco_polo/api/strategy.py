from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Strategy
from marco_polo.serializers import StrategySerializer
from django.contrib.auth.models import User
from knox.auth import TokenAuthentication


class AlgorithmAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            user = User.objects.get(username=self.request.user.username)
            strat = Strategy.objects.create(user=user)
            strat.strategy_file = request.data["strategy_file"]
            strat.save()
            return Response("Created Strategy", status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response("Could not create new strategy", status=status.HTTP_400_BAD_REQUEST)