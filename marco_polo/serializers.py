from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from .models import UserProfile, AlpacaAPIKeys, Strategy, StrategyVote, Universe, UsedUniverse, Backtest, BacktestTrade, Stock



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
    # fields that must be updated on first login
    username = serializers.CharField(allow_blank=False)
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)
    password = serializers.CharField(allow_blank=False)
    new_password = serializers.CharField(allow_blank=False)
    phone_number = serializers.CharField(allow_blank=False)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


class UpdateAuthUserSerializer(serializers.Serializer):
  first_name = serializers.CharField()
  last_name = serializers.CharField()
  username = serializers.CharField()
  password = serializers.CharField(required=False)
  new_password = serializers.CharField(required=False)

  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'username', 'password')
    extra_kwargs = {'password': {'write_only': True}}
  
  def update(self, instance, validated_data):
    instance.first_name = validated_data.get('first_name')
    instance.last_name = validated_data.get('last_name')
    instance.username = validated_data.get('username')
    new_pass = validated_data.get('new_password')
    old_pass = validated_data.get('password')
    if new_pass:
      if not instance.check_password(validated_data.get('password')):
        instance.save()
        return Response({"message": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
      instance.set_password(new_pass)
    instance.save()
    return instance


class UpdateProfileSerializer(serializers.Serializer):
  class Meta:
    model = UserProfile
    fields = ('firstlogin', 'avatar', 'phone_number')


class AlpacaKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlpacaAPIKeys
        fields = '__all__'


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = '__all__'


class StrategyVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategyVote
        fields = '__all__'


class UniverseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Universe
        fields = '__all__'


class UsedUniverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedUniverse
        fields = '__all__'


class BacktestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backtest
        fields = '__all__'


class BacktestTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacktestTrade
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = '__all__'