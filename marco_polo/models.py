from django.db import models
from django.contrib.auth.models import User
from fernet_fields import EncryptedTextField
import os
# Create your models here.


def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=None, null=True)
    description = models.TextField(max_length=None, null=True)
    strategy_file = models.FileField(
        upload_to='uploads/algos/', blank=True, null=True)
    approved = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)


class Stock(models.Model):
    symbol = models.CharField(max_length=6, primary_key=True)
    exchange = models.CharField(max_length=30)


class Universe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock, related_name='stocks')
    name = models.CharField(max_length=100, null=False, default='')
    updated = models.DateTimeField(auto_now_add=True, blank=True)


class UsedUniverse(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock)
    name = models.CharField(max_length=100, null=False, default='')
    updated = models.DateTimeField(auto_now_add=True, blank=True)


class Backtest(models.Model):
    id = models.AutoField(primary_key=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    universe = models.OneToOneField(
        UsedUniverse, on_delete=models.CASCADE, related_name='universe')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    successful = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    initial_cash = models.FloatField(null=False)
    end_cash = models.FloatField(default=initial_cash, null=False)
    sharpe = models.FloatField(null=False)
    vote_status = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)


class BacktestVote(models.Model):
    id = models.AutoField(primary_key=True)
    backtest = models.ForeignKey(
        Backtest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.BooleanField(default=None)


class BacktestTrade(models.Model):
    id = models.AutoField(primary_key=True)
    backtest = models.ForeignKey(Backtest, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=6, null=False)
    buy_time = models.DateTimeField(null=False)
    sell_time = models.DateTimeField(null=False)
    buy_price = models.FloatField(null=False)
    sell_price = models.FloatField(null=False)
    qty = models.IntegerField(null=False)


class LiveTradeInstance(models.Model):
    id = models.AutoField(primary_key=True)
    backtest = models.ForeignKey(Backtest, on_delete=models.CASCADE)
    pid = models.IntegerField(null=True)
    live = models.BooleanField(null=False, default=True)


class LiveTradeInstancePosition(models.Model):
    id = models.AutoField(primary_key=True)
    live_trade_instance = models.ForeignKey(LiveTradeInstance, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=6)
    open = models.BooleanField(default=False)
    open_date = models.DateTimeField(null=False)
    close_date = models.DateTimeField()
    qty = models.IntegerField(null=False)
    open_price = models.FloatField(null=False)
    close_price = models.FloatField()


