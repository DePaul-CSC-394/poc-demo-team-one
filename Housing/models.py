from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

# Create your models here.

class HousingListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sqFeet = models.FloatField(default=0)
    description = models.TextField(blank=True)
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    location = gis_models.PointField(null=True, blank=True, geography=True)

    #chatGPT helped figure out how to automatically add a point field based on provided lat long
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)

class HousingBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(HousingListing, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    end_date = models.DateTimeField(blank=True)

