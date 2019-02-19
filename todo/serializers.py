from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from fernet_fields import EncryptedTextField


from .models import Todo, UserProfile, AlpacaAPIKeys

class AlpacaKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlpacaAPIKeys
        fields = ('user_id', 'key_id', 'secret_key')

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('id', 'title', 'description', 'completed')

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        None,
                                        validated_data['password'])

        code = get_random_string(length=6, allowed_chars='1234567890')
        UserProfile.objects.create(user=user,code=code)
        return user

class ExtUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=False)

    class Meta:
        model = UserProfile
        exclude = ('code', 'code_created')

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")

class FirstLoginSerializer(serializers.Serializer):
    # todo add fields that should be updated on first login
    username = serializers.IntegerField()
    password = serializers.CharField(allow_blank=False)
    new_password = serializers.CharField(allow_blank=False)
    phone_number = serializers.CharField(allow_blank=False)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")