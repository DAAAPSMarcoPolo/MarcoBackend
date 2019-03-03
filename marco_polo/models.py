from django.db import models
from django.contrib.auth.models import User
from fernet_fields import EncryptedTextField
import os 
# Create your models here.

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    firstlogin = models.BooleanField(default=True)
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=20)
    code_created = models.DateTimeField(null=True)
    avatar = models.ImageField(upload_to='uploads/', blank=True, null=True)


class AlpacaAPIKeys(models.Model):
    id = models.IntegerField(primary_key=True)
    key_id = EncryptedTextField(max_length=None)
    secret_key = EncryptedTextField(max_length=120)


class Strategy(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    strategy_file = models.BinaryField()
    approved = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)


class StrategyVote(models.Model):
    id = models.AutoField(primary_key=True)
    strategy = models.ForeignKey(Strategy)
    user = models.ForeignKey(User)
    vote = models.BooleanField(default=False)


class Universe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    updated = models.DateTimeField(auto_now_add=True, blank=True)


class StockInUniverse(models.Model):
    id = models.AutoField(primary_key=True)
    universe = models.ForeignKey(Universe, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=6)


class UsedUniverse(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    updated = models.DateTimeField(auto_now_add=True, blank=True)


class StockInUsedUniverse(models.Model):
    id = models.AutoField(primary_key=True)
    used_universe = models.ForeignKey(UsedUniverse, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=6)


class Backtest(models.Model):
    id = models.AutoField(primary_key=True)
    strategy = models.ForeignKey(Strategy)
    universe = models.OneToOneField(UsedUniverse, on_delete=models.CASCADE, related_name='universe')
    user = models.ForeignKey(User)
    complete = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    initial_cash = models.FloatField(null=False)
    end_cash = models.FloatField(default=initial_cash, null=False)
    sharpe = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)


class BacktestTrade(models.Model):
    id = models.AutoField(primary_key=True)
    backtest = models.ForeignKey(Backtest)
    symbol = models.CharField(max_length=6, null=False)
    buy_time = models.DateTimeField(auto_now_add=True, blank=True)
    sell_time = models.DateTimeField(auto_now_add=True, blank=True)
    buy_price = models.FloatField(null=False)
    sell_price = models.FloatField(null=False)
    qty = models.IntegerField(null=False)






