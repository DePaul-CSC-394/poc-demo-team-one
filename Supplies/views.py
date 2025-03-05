from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.conf import settings
from .models import SupplyBooking, SupplyListing
from datetime import datetime
from django.utils.timezone import make_aware
import folium
import stripe
from .helpers import get_nearby_listings, get_available_listings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def supplies(request):
    supplies_list = SupplyListing.objects.all()  
    return render(request, 'Supplies/supplies.html', {'listings': supplies_list})

def detail (request, listing_id):

    listing = get_object_or_404(SupplyListing, pk=listing_id)

    center_lat = listing.latitude  + Decimal(0.007)
    center_lon = listing.longitude - Decimal(0.007)

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

    return render(request, 'Supplies/listing_details.html', context)


def create_checkout_session(request, listing_id):    
    listing = get_object_or_404(SupplyListing, pk=listing_id)
    
    checkin_date = request.GET.get('checkin')
    checkout_date = request.GET.get('checkout')
    
    if not checkin_date or not checkout_date:
        return JsonResponse({'error': 'Missing check-in or check-out date'}, status=400)
    
    # Convert naive datetime strings to time zone-aware datetime objects
    try:
        checkin_date_dt = make_aware(datetime.strptime(checkin_date, "%Y-%m-%d"))
        checkout_date_dt = make_aware(datetime.strptime(checkout_date, "%Y-%m-%d"))
    except ValueError as e:
        return JsonResponse({'error': f"Invalid date format: {e}"}, status=400)
    
    # Calculate the total number of days user is looking to stay
    num_days = (checkout_date_dt - checkin_date_dt).days
            
    # Calculate the total price for the stay
    total_price = int(listing.price * num_days * 100)

    # Check for booking conflicts
    if is_booking_conflict(listing_id, checkin_date_dt, checkout_date_dt):
        return JsonResponse({'error': 'Rental dates conflict with an existing rental.'}, status=400)
    
    
    # Ensure the image is properly formatted as an absolute URL
    def get_absolute_image_url(image_url):
        if image_url:
            image_url = str(image_url)  # Ensure it's a string
            if not image_url.startswith("http"):
                return request.build_absolute_uri(image_url)  # Convert relative to absolute
            return image_url  # Already absolute
        return None

    listing_image = get_absolute_image_url(listing.photo_1)
    
        
    # Checkout session using data from listings
    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'unit_amount': total_price, 
                'product_data': {
                    'name': str(listing.supplyName),
                    'images': [listing_image] if listing_image else [],
                },
            },
            'quantity': 1,
        }
    ]
    
    # Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],  
        line_items=line_items,
        mode='payment',
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
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        return HttpResponse(f"Error retrieving session: {e}", status=400)

    # Extract metadata
    listing_id = session.metadata.get('listing_id')
    checkin_date_str = session.metadata.get('checkin_date')
    checkout_date_str = session.metadata.get('checkout_date')

    if not listing_id or not checkin_date_str or not checkout_date_str:
        return HttpResponse("Invalid metadata.", status=400)
    
    try:
        checkin_date = make_aware(datetime.strptime(checkin_date_str, "%Y-%m-%d"))
        checkout_date = make_aware(datetime.strptime(checkout_date_str, "%Y-%m-%d"))
    except ValueError as e:
        return HttpResponse(f"Invalid date format: {e}", status=400)
    
    # Check for booking conflicts
    if is_booking_conflict(listing_id, checkin_date, checkout_date):
        return HttpResponse("Rental dates conflict with an existing rental.", status=400)

    # Get the user and listing
    try:
        user = request.user  # Ensure the user is authenticated
        listing = SupplyListing.objects.get(id=listing_id)

        # Create the booking
        SupplyBooking.objects.create(
            user=user,
            listing=listing,
            start_date=checkin_date,
            end_date=checkout_date,
            is_pending=True
        )
        return render(request, 'Supplies/checkout_success_supplies.html')
    except SupplyListing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)
    except Exception as e:
        return HttpResponse(f"Error creating booking: {e}", status=500)
    

def search(request):
    if request.method == 'POST':

        location = request.POST['location']
        mileRadius = request.POST['mile-radius']
        item = request.POST['item-name']
        start_date_str = request.POST['start_date']
        end_date_str = request.POST['end_date']
        
        if mileRadius:
            mileRadiusFlt = float(mileRadius)
        else:
            mileRadiusFlt = 1

        if not location:
            listings = SupplyListing.objects.all()
        else:
            # Test PostGIS (toggle the flag)
            settings.USE_POSTGIS = True
            listings_postgis = get_nearby_listings(location, mileRadiusFlt)

            listings = listings_postgis
        
        if start_date_str and end_date_str:
            try:
                desired_start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                desired_end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                listings = get_available_listings(listings, desired_start_date, desired_end_date)
            except ValueError as e:
                print(f"Date parsing error: {e}")

        if (len(item)>0):
            listings = [listing for listing in listings if listing.supplyName == item]

        context={
            'listings': listings,
        }

        return render(request, 'Supplies/supplies.html', context)
    
def is_booking_conflict(listing_id, checkin_date, checkout_date):
    """
    Check if there is a booking conflict for the given listing and dates.
    """
    # Query for overlapping bookings
    conflicting_bookings = SupplyBooking.objects.filter(
        listing_id=listing_id,
        start_date__lt=checkout_date,  # Existing booking starts before the new booking ends
        end_date__gt=checkin_date,     # Existing booking ends after the new booking starts
    ).exists()

    return conflicting_bookings