from django.conf.urls import include, url
from rest_framework import routers

from .api import TodoViewSet, AdminRegistrationAPI, AddUserAPI, LoginAPI, FirstLoginAPI, LoginFactorAPI, AlpacaKeysAPI, UserManagementAPI

router = routers.DefaultRouter()
router.register('todos', TodoViewSet, 'todos')

urlpatterns = [
  url("^", include(router.urls)),
  url("users/list/$", UserManagementAPI.as_view()),
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
  # Update the alpaca keys
  url("^alpaca/$", AlpacaKeysAPI.as_view()),
  # Get request for alpaca key
  url("^alpaca/(?P<user_id>\d+)$", AlpacaKeysAPI.as_view())

]