from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

from knox.models import AuthToken
from knox.auth import TokenAuthentication

from .models import Todo, UserProfile, AlpacaAPIKeys
from .serializers import TodoSerializer, CreateUserSerializer, UserSerializer, LoginUserSerializer, \
    FirstLoginSerializer, UserProfileSerializer, ExtUserProfileSerializer, AlpacaKeysSerializer, UpdateAuthUserSerializer

from .utils.messages import Utils

from django.contrib.auth.models import User

import traceback
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings

from twilio.rest import Client


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
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        username = request.data['username']
        password = request.data['password']
        msg = "Username: " + username + "\nPassword: " + password
        Utils.send_email(self, message=msg, subject="MarcoPolo Login Credentials", recipients=[username])
        # send out text
        users = User.objects.filter(is_active=True).select_related('profile').values('username',
                                                                                     'profile__phone_number')
        for u in users:
            print(u)
            client = Client(settings.TWILIO_ACC_SID, settings.TWILIO_AUTH_TOKEN)
            body = username + " has been removed from MarcoPolo 😩✌️"
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:" + e)
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
                "message": "first login",
                "token": AuthToken.objects.create(user)
            })
        # 2 factor
        else:
            # create code, send text and send to next page
            code = get_random_string(length=6, allowed_chars='1234567890')
            profile = UserProfile.objects.get(user=user)
            now = datetime.now()
            profile_serializer = ExtUserProfileSerializer(profile, data={"code": code, "code_created": now},
                                                          partial=True)
            try:
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()
            except Exception as err:
                traceback.print_exc()
            # send text
            client = Client(settings.TWILIO_ACC_SID, settings.TWILIO_AUTH_TOKEN)
            body = "Your MarcoPolo 2-factor code is: " + code
            message = client.messages.create(
                body=body,
                from_='8475586630',
                to=userData['profile']['phone_number']
            )
            return Response({
                "message": "code sent"
            })


class LoginFactorAPI(generics.GenericAPIView):
    """
      Check if code for given user is correct and respond with token
    """

    def post(self, request, *args, **kwargs):
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

        code = request.data['code']
        isAdmin = user.is_staff
        user = login_serializer.validated_data

        if code == user_prof.code:
            print("here")
            return Response({
                "message": "code correct",
                "token": AuthToken.objects.create(user),
                "isAdmin": isAdmin
            })
        else:
            return Response({
                "message": "incorrect code"
            })


class FirstLoginAPI(generics.GenericAPIView):
    serializer_class = FirstLoginSerializer

    """
      Update UserProfile on first login
        - given username and password
        - updating password and user profile
    """

    # TODO refactor
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authorized_user = serializer.validated_data
        # update auth_user
        user = User.objects.get(username=request.data['username'])
        user_serializer = UpdateAuthUserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response({
                "message": "UpdateAuthUserSerializer invalid."
            })
        profile = UserProfile.objects.get(user=user)
        request.data['firstlogin'] = False
        profile_serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response({
                "message": "UserProfileSerializer invalid."
            })
        return Response({
            "message": "profile updated."
        })


class AlpacaKeysAPI(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        """ Add an Alpaca key pair """
        try:
            user = User.objects.get(username=request.data['user_id'])
        except User.DoesNotExist:
            print("user DNE")

        serializer = AlpacaKeysSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            k = AlpacaKeysAPI(user_id=request.data['user_id'], key_id=request.data['key_id'],
                              secret_id=request.data['secret_id'])
            k.save()
            request.data['user_id'] = k.pk  # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """

        try:
            user = User.objects.get(username=request.data['user_id'])
        except User.DoesNotExist:
            print("user DNE")

        serializer = TodoSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            k = AlpacaKeysAPI(user_id=request.data['user_id'], key_id=request.data['key_id'],
                              secret_id=request.data['secret_id'])
            k.save()
            return Response(status=status.HTTP_200_OK)

class UserSettingsAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            # HOW TO GET USER FROM TOKEN: user = User.objects.get(username=self.request.user.username)
            user = User.objects.select_related('profile') \
            .values('username', 'first_name', 'last_name', 'profile__phone_number') \
            .get(username=self.request.user.username)
        except User.DoesNotExist:
            print("user DNE")
            return Response({"message": "could not find user."})
        return Response({ "user": user })
    
    def put(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user.username)
        profile = UserProfile.objects.get(user=user)
        
        user.username = request.data['username']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        profile.phone_number = request.data['phone_number']
        
        user.save()
        profile.save()

        return Response({ "message": "updated profile." })

class UserManagementAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    # send list of current users
    def get(self, request, *args, **kwargs):
        users = User.objects.values('username')
        return Response({"users": users})

    def delete(self, request, *args, **kwargs):
        # deactivate user
        username = request.data['username']
        print(username)
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()

        # send out text
        users = User.objects.filter(is_active=True).select_related('profile').values('username',
                                                                                     'profile__phone_number')
        for u in users:
            print(u)
            client = Client(settings.TWILIO_ACC_SID, settings.TWILIO_AUTH_TOKEN)
            body = username + " has been removed from MarcoPolo 😩✌️"
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:" + e)

        return Response({"message": "user deleted."})

class AlpacaKeysAPI(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        """ Add an Alpaca key pair """
        try:
            user = User.objects.get(id=request.data['user'])
        except User.DoesNotExist:
            print("user DNE")

        print(request.data)
        serializer = AlpacaKeysSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            print('saving')
            serializer.save()
            print('saved')
            return Response(request.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """

        try:
            user = User.objects.get(id=request.data['user'])
        except User.DoesNotExist:
            print("user DNE")
        try:
            api_key = AlpacaAPIKeys.objects.get(user_id=request.data['user'])
            api_key.key_id = request.data['key_id']
            api_key.secret_key = request.data['secret_key']
            api_key.save()
            return Response(status=status.HTTP_200_OK)

        except AlpacaAPIKeys.DoesNotExist:
            print("API Key not found")
            return Response("No API key associated with given user", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """ Update an Alpaca key pair """
        try:
            ApiKey = AlpacaAPIKeys.objects.get(user_id=kwargs['user_id'])
        except AlpacaAPIKeys.DoesNotExist:
            print("API Key not found")
            return Response("No API key associated with given user", status=status.HTTP_400_BAD_REQUEST)

        response = AlpacaKeysSerializer(ApiKey, context=self.get_serializer_context()).data

        return Response(response)