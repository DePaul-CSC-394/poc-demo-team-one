from django.shortcuts import render
from .models import HousingListing
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from django.db.models import F, Func, FloatField, Value


# Create your views here.

def listings(request):
    listings = HousingListing.objects.all()

    context={
        'listings': listings
    }

    return render(request, 'Housing/listings.html', context)

def search(request):
    if request.method == 'POST':

        location = request.POST['location']
        mileRadius = request.POST['mile-radius']

        if mileRadius:
            mileRadiusFlt = float(mileRadius)
        else:
            mileRadiusFlt = 0

        listings = get_nearby_listings(location, mileRadiusFlt)

        context={
            'listings': listings,
        }

        return render(request, 'Housing/listings.html', context)
    
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  #earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def get_nearby_listings(location_name, radius_miles=10):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(location_name)
    
    if not location:
        return HousingListing.objects.none()
    
    lat, lon = location.latitude, location.longitude

    # Filter using Haversine formula in Python
    listings = HousingListing.objects.all()
    nearby_listings = [
        listing for listing in listings 
        if haversine(lat, lon, float(listing.latitude), float(listing.longitude)) <= radius_miles
    ]
    
    return nearby_listings