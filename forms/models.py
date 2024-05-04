from django.db import models
from account.models import User

# Create your models here.

class Ride(models.Model):
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    price = models.FloatField()

class Booking(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    price = models.FloatField()
    booking_time = models.TimeField()
    date = models.DateField(null=True)
    payed = models.BooleanField(default=False)
    payment_ref = models.CharField(blank=True,null=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
