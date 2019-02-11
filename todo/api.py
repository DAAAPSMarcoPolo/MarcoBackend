from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response

from knox.models import AuthToken
from knox.auth import TokenAuthentication

from .models import Todo
from .serializers import TodoSerializer, CreateUserSerializer, UserSerializer, LoginUserSerializer, UserProfileSerializer

from .utils.messages import Utils

class TodoViewSet(viewsets.ModelViewSet):
  permission_classes = [permissions.IsAuthenticated, ]
  serializer_class = TodoSerializer

  def get_queryset(self):
    return self.request.user.todos.all()

# TODO remove in production
class AdminRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })

class AddUserAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,permissions.IsAdminUser)

    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        username = request.data['username']
        password = request.data['password']
        msg = "Username: " + username + "\nPassword: " + password
        Utils.send_email(self, message=msg, subject="MarcoPolo Login Credentials", recipients=[username])
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        print(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            #"user_profile": UserProfileSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })