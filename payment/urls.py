from django.urls import re_path as url
from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/make-payment', MakePaymentApiView.as_view()), 
    path('api/verify-payment/<pk>', VerifyPaymentApiView.as_view()), 

]