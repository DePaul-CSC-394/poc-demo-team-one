from django.shortcuts import render
from .models import HousingListing
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

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
        
        if mileRadius:
            mileRadiusFlt = float(mileRadius)
        else:
            mileRadiusFlt = 0
        print(location)
        listings = get_nearby_listings(location, mileRadiusFlt)
        
        if start_date_str and end_date_str:
            try:
                desired_start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                desired_end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                listings = get_available_listings(listings, desired_start_date, desired_end_date)
            except ValueError as e:
                print(f"Date parsing error: {e}")

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
    except GeocoderUnavailable or GeocoderTimedOut:
        print("Error")
        return HousingListing.objects.none()
    
    if not location:
        return HousingListing.objects.none()
    
    lat, lon = location.latitude, location.longitude
    print(lat,lon)

    # Filter using Haversine formula in Python
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