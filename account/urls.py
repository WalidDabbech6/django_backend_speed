from django.urls import path
from .views import LoginApi,RegisterApi,VerifyOTP,UpdateProfileView


urlpatterns = [
      path('api/login', LoginApi.as_view(), name="login"),
      path('api/register', RegisterApi.as_view(), name='auth_register'),
      path('api/verify', VerifyOTP.as_view()),
      path('api/updateProfile', UpdateProfileView.as_view(),name='auth_update_profile'),


]