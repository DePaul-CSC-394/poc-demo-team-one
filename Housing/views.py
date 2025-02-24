from decimal import Decimal
import random
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from UniVerse import settings
from .models import HousingBooking, HousingListing
from .helpers import get_available_listings, get_nearby_listings, get_type_listings
import datetime
import folium
import stripe
from django.contrib.auth.models import User

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
    

    #from documentation: https://python-visualization.github.io/folium/latest/user_guide.html
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
    
    checkin_date = request.GET.get('checkin')
    checkout_date = request.GET.get('checkout')
    
    if not checkin_date or not checkout_date:
        return JsonResponse({'error': 'Missing check-in or check-out date'}, status=400)
    
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
                    'name': str(listing.home_type) + " #"+ str(listing_id),
                    # You can add more product details here if you want
                    'images': [listing.photo_1] if listing.photo_1 else [],
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
        success_url=request.build_absolute_uri(reverse('success')) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('listing-details', kwargs={'listing_id': listing_id})),
        metadata={
            'listing_id': listing_id,
            'checkin_date': checkin_date,
            'checkout_date': checkout_date,
        }
        # shipping_address_collection={'allowed_countries': ['US']},
        # automatic_tax={'enabled': True}, # if using Stripe Tax
    )

    return redirect(session.url, code=303)

def success(request):
    # Retrieve the session ID from the query parameters
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponse("Session ID not found.", status=400)

    # Retrieve the session from Stripe
    session = stripe.checkout.Session.retrieve(session_id)

    # Extract metadata
    listing_id = session.metadata.get('listing_id')
    checkin_date = session.metadata.get('checkin_date')
    checkout_date = session.metadata.get('checkout_date')

    if not listing_id or not checkin_date or not checkout_date:
        return HttpResponse("Invalid metadata.", status=400)

    # Get the user and listing
    user = request.user
    listing = HousingListing.objects.get(id=listing_id)

    # Create the booking
    HousingBooking.objects.create(
        user=user,
        listing=listing,
        start_date=checkin_date,
        end_date=checkout_date,
        is_pending=True
    )
        
    return render(request, 'Housing/checkout_success.html')




