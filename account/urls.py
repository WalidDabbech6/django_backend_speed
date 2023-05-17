from django.urls import re_path as url
from django.urls import path, include
from .views import *


urlpatterns = [
      path('api/login', LoginApi.as_view()),
      path('api/register', RegisterApi.as_view(), name='auth_register'),
      path('api/verify', VerifyOTP.as_view()),
      path('api/updateProfile', UpdateProfileView.as_view(),name='auth_update_profile'),


]