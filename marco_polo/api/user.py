from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework import status
from knox.auth import TokenAuthentication
from marco_polo.models import UserProfile
from django.contrib.auth.models import User
from django.conf import settings
from twilio.rest import Client


class PictureAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            user = User.objects.get(username=self.request.user.username)
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist or User.DoesNotExist:
            print("user DNE")
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(profile.avatar.url, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user = User.objects.get(username=self.request.user.username)
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist or User.DoesNotExist:
            print("user DNE")
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile.avatar = request.data['avatar']
        user.save()
        profile.save()
        return Response(status=status.HTTP_200_OK)


class UserSettingsAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.select_related('profile') \
                .values('username', 'first_name', 'last_name', 'profile__phone_number') \
                .get(username=self.request.user.username)
        except User.DoesNotExist:
            print("user DNE")
            return Response({"message": "could not find user."})
        return Response({"user": user})

    def put(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user.username)
        profile = UserProfile.objects.get(user=user)

        user.username = request.data['username']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        profile.phone_number = request.data['phone_number']

        # TODO save password
        if 'new_password' in request.data:
            password = request.data['password']
            if not user.check_password(password):
                return Response({"message": "invalid password."})
            new_password = request.data['new_password']
            user.set_password(new_password)

        user.save()
        profile.save()

        return Response({"message": "updated profile."})


class UserManagementAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    # send list of current users
    def get(self, request, *args, **kwargs):
        users = User.objects.values('username', 'is_active', 'is_staff')
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
            client = Client(settings.TWILIO_ACC_SID,
                            settings.TWILIO_AUTH_TOKEN)
            body = username + " has been removed from marco_polo 😩✌️"
            try:
                client.messages.create(
                    body=body,
                    from_='8475586630',
                    to=u['profile__phone_number']
                )
            except Exception as e:
                print("Twilio error:")
                print(e)

        return Response({"message": "user deleted."})
