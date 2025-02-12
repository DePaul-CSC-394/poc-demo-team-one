from django.shortcuts import render

from UniVerse import settings
from .models import HousingListing
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
import time
from django.contrib.gis.measure import D


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
        start_date_str = request.POST['start_date']
        end_date_str = request.POST['end_date']
        home_type = request.POST['home_type']
        
        if mileRadius:
            mileRadiusFlt = float(mileRadius)
        else:
            mileRadiusFlt = 1
        # Test haversine (ensure it's not using PostGIS)
        # settings.USE_POSTGIS = False
        # start = time.time()
        # listings_haversine = get_nearby_listings(location, mileRadiusFlt)
        # elapsed_haversine = time.time() - start
        # print(f"Haversine method took {elapsed_haversine:.4f} seconds")


        if not location:
            listings = HousingListing.objects.all()
        else:
            # Test PostGIS (toggle the flag)
            settings.USE_POSTGIS = True
            # start = time.time()
            listings_postgis = get_nearby_listings(location, mileRadiusFlt)
            # elapsed_postgis = time.time() - start
            # print(f"PostGIS method took {elapsed_postgis:.4f} seconds")

            listings = listings_postgis
        
        if start_date_str and end_date_str:
            try:
                desired_start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                desired_end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                listings = get_available_listings(listings, desired_start_date, desired_end_date)
            except ValueError as e:
                print(f"Date parsing error: {e}")

        if home_type and home_type !="Home Types":
            listings=get_type_listings(listings, home_type)

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
    try:
        location = geolocator.geocode(location_name)
    except (GeocoderUnavailable, GeocoderTimedOut) as e:
        print("Error")
        return HousingListing.objects.none()
    
    if not location:
        return HousingListing.objects.none()
    
    lat, lon = location.latitude, location.longitude
    print(lat,lon)

    if settings.USE_POSTGIS:
        #https://alldjango.com/articles/searching-within-area-geodjango-postgis
        user_location = Point(lon, lat, srid=4326)
        #annotate adds extra distance column
        return HousingListing.objects.annotate(
            distance=Distance("location", user_location)
        ).filter(distance__lte=D(mi=radius_miles))
    else:
        listings = HousingListing.objects.all()
        nearby_listings = [
            listing for listing in listings 
            if haversine(lat, lon, float(listing.latitude), float(listing.longitude)) <= radius_miles
        ]
        return nearby_listings



def get_available_listings(nearby_listings, desired_start_date, desired_end_date):
    """
    Filters a list of listings and returns only those that are available 
    between desired_start_date and desired_end_date.
    """
    available_listings = []
    for listing in nearby_listings:
        # Check for any booking that overlaps with the desired dates.
        # Overlap exists if: booking.start_date < desired_end_date and booking.end_date > desired_start_date.
        if not listing.housingbooking_set.filter(
            start_date__lt=desired_end_date,
            end_date__gt=desired_start_date
        ).exists():
            available_listings.append(listing)
    return available_listings


def get_type_listings(listings, home_type):
    type_listings=[]

    for listing in listings:
        if listing.home_type==home_type:
            type_listings.append(listing)


    return type_listings