from django.shortcuts import get_object_or_404, render
from UniVerse import settings
from .models import HousingListing
from .helpers import get_available_listings, get_nearby_listings, get_type_listings
import datetime

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
    


def detail (request, listing_id):

    listing = get_object_or_404(HousingListing, pk=listing_id)

    context = {
        'listing' : listing
    }

    return render(request, 'Housing/listing_details.html', context)
