from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from django.http import JsonResponse

from aymenProject.pagination import PageNumberPaginationDataOnly
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
import random
import string
import json
import datetime



    

class RidesView(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = RideSerilizer
    def get_queryset(self):
        return Ride.objects.all()
    def post(self,request):     
        origin_shift = request.data["origin"];
        destination_shift = request.data["destination"]
        if (request.data["origin"] != "TUN"):
            origin_shift = request.data["destination"]
            destination_shift = request.data["origin"]
        ride = Ride.objects.get(origin=origin_shift,destination=destination_shift)
        return Response(RideSerilizer(ride).data,status=status.HTTP_200_OK) 
    

class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPaginationDataOnly
    def get_queryset(self):
        return Booking.objects.all().filter(user_id=self.request.user)
    def post(self,request):
        origin_shift = request.data["origin"];
        destination_shift = request.data["destination"]
        price = request.data["price"]
        time = request.data["time"]
        date = datetime.datetime.strptime(request.data["date"], settings.DATE_FORMAT).date()
        if (request.data["origin"] != "TUN"):
            origin_shift = request.data["destination"]
            destination_shift = request.data["origin"]
        ride = Ride.objects.get(origin=origin_shift,destination=destination_shift)
        user = User.objects.get(email=self.request.user)
        booking = Booking(ride=ride,user=user,price=price,booking_time=time,date=date)
        booking.save()
        return Response(BookingSerializer(booking).data,status=status.HTTP_201_CREATED) 



class BookingRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        # Retrieve the authenticated user making the request
        user = self.request.user
        
        # Filter the queryset to include only bookings associated with the user
        queryset = Booking.objects.filter(user=user)
        
        return queryset