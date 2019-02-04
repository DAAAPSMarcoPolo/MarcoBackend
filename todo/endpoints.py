from django.conf.urls import include, url
from rest_framework import routers

from .api import TodoViewSet, RegistrationAPI, LoginAPI

router = routers.DefaultRouter()
router.register('todos', TodoViewSet, 'todos')

urlpatterns = [
  url("^", include(router.urls)),
  url("^auth/register/$", RegistrationAPI.as_view()),
  url("^auth/login/$", LoginAPI.as_view())
]