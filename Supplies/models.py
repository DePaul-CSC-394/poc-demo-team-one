from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim

from django.db import models

# Create your models here.

class SupplyListing(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    supplyName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, max_length=500)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, max_length=500)
    pickupLocation = gis_models.PointField(null=True, blank=True, geography=True)
    city_state = models.TextField(blank=True)

    #chatGPT helped figure out how to automatically add a point field based on provided lat long
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)

        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.reverse(f"{self.latitude}, {self.longitude}", exactly_one=True)
        address = location.raw.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village') or ""
        state = address.get('state') or ""
        self.city_state =  f"{city}, {state}"
        super().save(*args, **kwargs)

class SupplyBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(SupplyListing, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    end_date = models.DateTimeField(blank=True)
    is_pending=models.BooleanField(blank=True, default=True)
    was_denied=models.BooleanField(blank=True, default=True)

