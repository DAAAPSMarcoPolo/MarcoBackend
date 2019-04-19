from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from marco_polo.models import UserProfile, AlpacaAPIKeys
from marco_polo.serializers import CreateUserSerializer, UserSerializer, LoginUserSerializer, \
    FirstLoginSerializer, UserProfileSerializer, ExtUserProfileSerializer, AlpacaKeysSerializer, UpdateAuthUserSerializer
from marco_polo.utils.messages import Utils
from django.contrib.auth.models import User
import traceback
import re
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from twilio.rest import Client


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
        # regex to check email
        pattern = re.compile("^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$")
        if not pattern.match(username):
            return Response({
                "error": "invalid email address"
            }, status=status.HTTP_400_BAD_REQUEST)
        msg = "Username: " + username + "\nPassword: " + password
        Utils.send_email(
            self, message=msg, subject="marco_polo Login Credentials", recipients=[username])
        # TODO test
        # send out text
        users = User.objects.filter(is_active=True).select_related('profile').values('username',
                                                                                     'profile__phone_number')
        for u in users:
            print(u)
            client = Client(settings.TWILIO_ACC_SID,
                            settings.TWILIO_AUTH_TOKEN)
            body = username + " has been added to marco_polo 🤗😎"
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:")
                print(e)
        # TODO change this, don't know why we sending token...
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
        userData = UserSerializer(
            user, context=self.get_serializer_context()).data
        print(userData)
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
            client = Client(settings.TWILIO_ACC_SID,
                            settings.TWILIO_AUTH_TOKEN)
            body = "Your marco_polo 2-factor code is: " + code
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
        userData = User.objects.get(id=user.id)

        if code == user_prof.code:
            return Response({
                "message": "code correct",
                "token": AuthToken.objects.create(user),
                "isAdmin": isAdmin,
                "user": {
                    'id': userData.id,
                    'first_name': userData.first_name,
                    'last_name': userData.last_name
                }
            })
        else:
            return Response({
                "error": "incorrect code"
            }, status=status.HTTP_400_BAD_REQUEST)


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
        user_serializer = UpdateAuthUserSerializer(
            user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response({
                "message": "UpdateAuthUserSerializer invalid."
            })
        profile = UserProfile.objects.get(user=user)
        request.data['firstlogin'] = False
        profile_serializer = UserProfileSerializer(
            profile, data=request.data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response({
                "message": "UserProfileSerializer invalid."
            })
        return Response({
            "message": "profile updated."
        })
