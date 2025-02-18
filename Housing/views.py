from decimal import Decimal
import random
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from UniVerse import settings
from .models import HousingListing
from .helpers import get_available_listings, get_nearby_listings, get_type_listings
import datetime
import folium
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

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

    offset_range = 0.01

    # make the location "approximate"
    center_lat = listing.latitude  + Decimal(random.uniform(-offset_range, offset_range))
    center_lon = listing.longitude + Decimal(random.uniform(-offset_range, offset_range))


    # Create the map object
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, zoom_control=False, scrollWheelZoom=False, tiles="openstreetmap", dragging=False, doubleClickZoom=False)

    # Add markers (optional, for specific locations)
    # folium.Marker([listing.latitude, listing.longitude], popup="Location Name").add_to(m)
    radius = 100
    folium.CircleMarker(
        location=[center_lat, center_lon],
        radius=radius,
        color="cornflowerblue",
        fill=True,
        fill_opacity=0.6,
        opacity=1,
    ).add_to(m)

    # Get the HTML representation of the map
    map_html = m._repr_html_()



    context = {
        'listing' : listing,
        'map_html': map_html,
    }

    return render(request, 'Housing/listing_details.html', context)


def create_checkout_session(request, listing_id):
    listing = get_object_or_404(HousingListing, pk=listing_id)
    # Checkout session using data from listings
    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(listing.price)*100, 
                'recurring': {
                    'interval': 'month',  # monthly subscription
                },
                'product_data': {
                    'name': listing.description or "Housing Subscription",
                    # You can add more product details here if you want
                },
            },
            'quantity': 1,
        }
    ]
    
    # Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],  
        line_items=line_items,
        mode='subscription',
        allow_promotion_codes=True,  # displays "Add promotion code" link
        billing_address_collection='required',
        success_url=request.build_absolute_uri(reverse('success')),
        cancel_url=request.build_absolute_uri(reverse('listing-details', kwargs={'listing_id': listing_id})),
        # shipping_address_collection={'allowed_countries': ['US']},
        # automatic_tax={'enabled': True}, # if using Stripe Tax
    )

    return redirect(session.url, code=303)

def success(request):
    return render(request, 'Housing/checkout_success.html')



