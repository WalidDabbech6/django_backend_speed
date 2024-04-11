from django.urls import re_path as url
from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/rides', RidesView.as_view()), 
    path('api/bookings', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingRetrieveUpdateAPIView.as_view(), name='booking-retrieve-update'),



   
]