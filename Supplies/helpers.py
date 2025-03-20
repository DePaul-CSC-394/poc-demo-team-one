from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
import time
from django.contrib.gis.measure import D
from .models import SupplyListing
from UniVerse import settings

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
        print(e)
        return SupplyListing.objects.none()
    
    if not location:
        return SupplyListing.objects.none()
    
    lat, lon = location.latitude, location.longitude
    print(lat,lon)

    if settings.USE_POSTGIS:
        #https://alldjango.com/articles/searching-within-area-geodjango-postgis
        user_location = Point(lon, lat, srid=4326)
        #annotate adds extra distance column
        return SupplyListing.objects.annotate(
            distance=Distance("pickupLocation", user_location)
        ).filter(distance__lte=D(mi=radius_miles))
    else:
        listings = SupplyListing.objects.all()
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
        if not listing.supplybooking_set.filter(
            start_date__lt=desired_end_date,
            end_date__gt=desired_start_date
        ).exists():
            available_listings.append(listing)
    return available_listings