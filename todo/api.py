from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response

from knox.models import AuthToken
from knox.auth import TokenAuthentication

from .models import Todo, UserProfile
from .serializers import TodoSerializer, CreateUserSerializer, UserSerializer, LoginUserSerializer, FirstLoginSerializer, UserProfileSerializer, ExtUserProfileSerializer

from .utils.messages import Utils

from django.contrib.auth.models import User

import traceback
from datetime import datetime
from django.utils.crypto import get_random_string

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
        userData = UserSerializer(user, context=self.get_serializer_context()).data
        # only send token if not firstlogin
        if userData['profile']['firstlogin']:
          return Response({
            "user": userData,
          })
        else:
          # TODO 2 factor things...
          # create code, send text and send to next page
          code = get_random_string(length=6, allowed_chars='1234567890')
          profile = UserProfile.objects.get(user=user)
          now = datetime.now()
          profile_serializer = ExtUserProfileSerializer(profile, data={ "code": code, "code_created": now}, partial=True)
          try:
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
          except Exception as err:
            traceback.print_exc()
          return Response({
            "user": userData,
            "token": AuthToken.objects.create(user)
          })
        
        

class FirstLoginAPI(generics.GenericAPIView):
  """
    Update UserProfile on first login
      - given username and password
      - updating password and user profile
  """
  # TODO refactor
  def post(self, request, *args, **kwargs):
    # find user
    print("Finding a user..." + request.data['username'])
    try:
      user = User.objects.get(username=request.data['username'])
    except User.DoesNotExist:
      print("user DNE")
    login_serializer = LoginUserSerializer(data=request.data)
    profile_serializer = UserProfileSerializer(data=request.data)
    if not login_serializer.is_valid(raise_exception=ValueError):
      print("There was an error validating the user (login serializer)")
    print("get instance of profile object...")
    # get instance of profile object
    user_prof = UserProfile.objects.get(user=user)
    print(user_prof.user_id)
    profile_serializer = UserProfileSerializer(user_prof, data=request.data, partial=True)
    if profile_serializer.is_valid(raise_exception=ValueError):
      # update password
      user = login_serializer.validated_data
      user.set_password(profile_serializer.validated_data['new_password'])
      user.save()
      # update profile info
      profile_serializer.save()
      return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)
        })
    # TODO better response...
    return Response({
      "user": user,
      "error": "there was an error"
    }, status=status.HTTP_400_BAD_REQUEST)
