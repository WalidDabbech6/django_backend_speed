from rest_framework import serializers
from .models import *
from django.conf import settings
    

class RideSerilizer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField('get_origin')
    destination = serializers.SerializerMethodField('get_destination')
    price = serializers.SerializerMethodField('get_price')
   
    class Meta:
        model = Ride
        exclude = ('id',)
    def get_origin(self, obj):
        return obj.origin
    def get_destination(self,obj):
        return obj.destination
    def get_price(self,obj):
        print(self)
        return obj.price



class BookingSerializer(serializers.ModelSerializer):
    ride = RideSerilizer()
    date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS ,format=settings.DATE_FORMAT)
    def to_representation(self, instance):
        
        # Convert created_at field to a more elegant string format
        created_at = instance.created_at.strftime('%d %B , %Y %H:%M')

        # Get the original representation
        representation = super().to_representation(instance)

        # Update the created_at field in the representation
        representation['created_at'] = created_at

        return representation

    class Meta:
        model = Booking
        fields = ['id', 'user', 'ride','price','booking_time','created_at','date','payed','payment_ref']
        
     