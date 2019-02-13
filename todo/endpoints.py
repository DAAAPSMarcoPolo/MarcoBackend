from django.conf.urls import include, url
from rest_framework import routers

from .api import TodoViewSet, AdminRegistrationAPI, AddUserAPI, LoginAPI, FirstLoginAPI

router = routers.DefaultRouter()
router.register('todos', TodoViewSet, 'todos')

urlpatterns = [
  url("^", include(router.urls)),
  url("^auth/adduser/$", AddUserAPI.as_view()),
  
  # TODO remove in production
  url("^auth/register/admin/$", AdminRegistrationAPI.as_view()),

  url("^auth/login/$", LoginAPI.as_view()),
  url("^auth/firstlogin/$", FirstLoginAPI.as_view())
]