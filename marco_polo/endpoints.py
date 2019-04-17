from django.conf.urls import include, url
from rest_framework import routers

from marco_polo.api.login import AdminRegistrationAPI, AddUserAPI, LoginAPI, FirstLoginAPI, LoginFactorAPI
from marco_polo.api.user import UserManagementAPI, PictureAPI, UserSettingsAPI
from marco_polo.api.api_keys import AlpacaKeysAPI
from marco_polo.api.strategy import AlgorithmAPI, StrategyAPI
from marco_polo.api.universe import UniverseAPI
from marco_polo.api.alpaca import SeedAPI
from marco_polo.api.stock import StockAPI
from marco_polo.api.backtest import BacktestAPI
from marco_polo.api.live import LiveAPI, StrategyLiveInstanceAPI
from marco_polo.api.backtest import BacktestVoteAPI
from marco_polo.api.strategy_backtests import StrategyBacktests
from marco_polo.api.tradelogs import TradeLogsAPI

router = routers.DefaultRouter()

urlpatterns = [
  url("^", include(router.urls)),
  url("users/list/$", UserManagementAPI.as_view()),
  url("user/settings/$", UserSettingsAPI.as_view()),
  url("^auth/adduser/$", AddUserAPI.as_view()),
  # TODO remove in production
  # register the admin initially
  url("^auth/register/admin/$", AdminRegistrationAPI.as_view()),
  # login with username/password
  url("^auth/login/$", LoginAPI.as_view()),
  # login with code
  url("^auth/loginfactor/$", LoginFactorAPI.as_view()),
  # update profile on first login
  url("^auth/firstlogin/$", FirstLoginAPI.as_view()),
  # Get the profile picture
  url("^profilepicture/$", PictureAPI.as_view()),
  # Update the alpaca keys
  url("^alpaca/$", AlpacaKeysAPI.as_view()), 
  # Manage strategy python files 
  url("^algofile/$", AlgorithmAPI.as_view()),
  # Manage universes
  url("^universe/$", UniverseAPI.as_view()),
  url("^universe/(?P<id>\d+)/$", UniverseAPI.as_view()),
  # Only to seed the db with tradable stocks
  url("^stockseed/$", SeedAPI.as_view()),
  # Get all algos
  url("^algorithm/$", StrategyAPI.as_view()),
  url("^algorithm/(?P<id>\d+)/$", StrategyAPI.as_view()),
  # Get stocks
  url("^stocks/$", StockAPI.as_view()),
  url("^stocks/(?P<input>[\w\-]+)/$", StockAPI.as_view()),
  # Run backtest
  url("^backtest/$", BacktestAPI.as_view()),
  url("^backtest/(?P<id>\d+)/$", BacktestAPI.as_view()),
  url("^backtest/(?P<id>\d+)/live$", BacktestVoteAPI.as_view()),
  url("^strategybacktests/(?P<id>\d+)/$", StrategyBacktests.as_view()),
  url("^live/$", LiveAPI.as_view()),
  url("^live/(?P<id>\d+)/$", LiveAPI.as_view()),
  url("^strategyliveinstances/(?P<id>\d+)/$", StrategyLiveInstanceAPI.as_view()),
  url("^tradelogs/$", TradeLogsAPI.as_view()),
  url("^tradelogs/(?P<id>\d+)/$", TradeLogsAPI.as_view())
]
