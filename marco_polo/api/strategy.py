from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework import status
from marco_polo.models import Strategy
from marco_polo.models import Backtest
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
            print(request.data["strategy_file"])
            strat.strategy_file = request.data["strategy_file"]
            strat.name = request.data["name"]
            strat.description = request.data["description"]
            strat.save()
            return Response("Created Strategy", status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response("Could not create new strategy", status=status.HTTP_400_BAD_REQUEST)


# /algorithm/<id>
class StrategyAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # GET single algorithm details
        if 'id' in kwargs:
            try:
                id = self.kwargs['id']
                print(id)
                algo = Strategy.objects.values(
                    'name', 'description', 'user', 'created_at', 'approved').get(id=id)
                backtest_list = Backtest.objects.filter(
                    strategy=id).values()
                data = {
                    'algo_details': algo,
                    'bt_list': backtest_list
                }

                return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response("Could not get the details for that algo", status=status.HTTP_400_BAD_REQUEST)
        # GET list of algos
        try:
            all_strats = Strategy.objects.all().values(
                'id', 'name', 'description', 'user', 'created_at', 'approved')
            return Response(all_strats, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response("Could not get all of the algos", status=status.HTTP_400_BAD_REQUEST)
