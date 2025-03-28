from django.shortcuts import get_object_or_404, render, redirect
from Supplies.models import SupplyListing, SupplyBooking, SupplyReview
from UniVerse import settings
from Housing.models import HomeReview, HousingListing, HousingBooking
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Create your views here.

def dashboard(request):
    
    user=request.user

    if not user.is_authenticated:
        return redirect('login')
        
    user_listings=HousingListing.objects.filter(user=user)

    for listing in user_listings:
        listing.pendings=list(
            HousingBooking.objects.filter(listing=listing, is_pending=True)
        )
        
    user_supply_listings=SupplyListing.objects.filter(user=user)

    for supply in user_supply_listings:
        supply.pendings=list(
            SupplyBooking.objects.filter(listing=supply, is_pending=True)
        )
    user_bookings=HousingBooking.objects.filter(user=user)

    user_supply_bookings=SupplyBooking.objects.filter(user=user)

    return render(request, 'Dashboard/dashboard.html', {'user_listings': user_listings, 
        'user_bookings': user_bookings, 'user_supply_listings': user_supply_listings, 'user_supply_bookings': user_supply_bookings})

def add_listing(request):
    if request.method == 'POST':
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        photo4 = request.FILES.get('photo4')
        home_type = request.POST.get('homeType')
        address = request.POST.get('address')
        bedrooms = int(request.POST.get('bedrooms', 0))
        bathrooms = float(request.POST.get('bathrooms', 0))
        sqFeet = float(request.POST.get('sqFeet', 0))
        description = request.POST.get('description')
        price = float(request.POST.get('price', 0))

        # Geocode the address to get latitude and longitude
        geolocator = Nominatim(user_agent="my_app")
        try:
            location = geolocator.geocode(address, timeout=10)  # Geocode the address
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                # Handle case where address cannot be geocoded
                return render(request, 'Dashboard/add_listing.html', {
                    'error': 'Unable to geocode the provided address. Please check the address and try again.'
                })
        except GeocoderTimedOut:
            return render(request, 'Dashboard/add_listing.html', {
                'error': 'Geocoding service timed out. Please try again.'
            })

        listing = HousingListing(
            user=request.user,
            photo_1=photo1 if photo1 else None,
            photo_2=photo2 if photo2 else None,
            photo_3=photo3 if photo3 else None,
            photo_4=photo4 if photo4 else None,
            home_type=home_type,
            latitude=latitude,
            longitude=longitude,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            sqFeet=sqFeet,
            description=description,
            price=price
        )

        listing.save()

        listing.photo_1 = "/media/" + str(listing.photo_1)
        listing.photo_2 = "/media/" + str(listing.photo_2)
        if photo3:
            listing.photo_3 = "/media/" + str(listing.photo_3)
        if photo4:
            listing.photo_4 = "/media/" + str(listing.photo_4)
        listing.save()

        return redirect('dashboard')  # Redirect to dashboard after submission

    return render(request, 'Dashboard/add_listing.html')


def approve_or_deny (request):
    if request.method == 'POST':
        booking_id=request.POST.get('booking_id')
        action=request.POST.get('action')
        listing_type = request.POST.get('type')
        if listing_type == 'housing':
            booking = get_object_or_404(HousingBooking, id=booking_id)
            user_email=booking.user.email
        else:
            booking = get_object_or_404(SupplyBooking, id=booking_id)
            user_email=booking.user.email

        subject=''
        message=''

        if action == 'approve':
            booking.is_pending=False
            booking.was_denied=False
            subject="Your Booking Has Been Approved"
            message=f"Dear {booking.user.username}, \n\n Your booking has been approved. You may proceed with the next steps."

        elif action == 'deny':
            booking.is_pending=False
            booking.was_denied=True
            subject="Your Booking Has Been Denied"
            message=f"Dear {booking.user.username}, \n\n Unfortunately, your booking has been denied."

        
        booking.save()

        send_mail(
            subject,
            message,
            'UniVerse@example.com',
            [user_email],
            fail_silently=True
        )
        return redirect('dashboard')

    return redirect('dashboard')


def delete_listing(request, listing_id):
    # Ensure the user can only delete their own listings
    listing = get_object_or_404(HousingListing, id=listing_id, user=request.user)

    # Delete the listing
    listing.delete()

    # Redirect back to the dashboard
    return redirect('dashboard')

def add_supplies(request): 

    if request.method == 'POST':
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        photo4 = request.FILES.get('photo4')
        supplyName = request.POST.get('supplyname')
        condition = request.POST.get('conditionType')
        pickup = request.POST.get('pickupLocation')
        description = request.POST.get('description')
        price = float(request.POST.get('price', 0))

        # Geocode the address to get latitude and longitude
        geolocator = Nominatim(user_agent="my_app")
        try:
            s_location = geolocator.geocode(pickup, timeout=10)  # Geocode the address
            if s_location:
                s_latitude = s_location.latitude
                s_longitude = s_location.longitude
            else:
                # Handle case where address cannot be geocoded
                return render(request, 'Dashboard/add_supplies.html', {
                    'error': 'Unable to geocode the provided address. Please check the address and try again.'
                })
        except GeocoderTimedOut:
            return render(request, 'Dashboard/add_supplies.html', {
                'error': 'Geocoding service timed out. Please try again.'
            })

        supply = SupplyListing(
            user=request.user,
            supplyName=supplyName,
            condition=condition,
            description=description,
            price=price,
            latitude=s_latitude,
            longitude=s_longitude,
            photo_1=photo1 if photo1 else None,
            photo_2=photo2 if photo2 else None,
            photo_3=photo3 if photo3 else None,
            photo_4=photo4 if photo4 else None,
        )

        supply.save()

        supply.photo_1 = "/media/" + str(supply.photo_1)
        supply.photo_2 = "/media/" + str(supply.photo_2)
        if photo3:
            supply.photo_3 = "/media/" + str(supply.photo_3)
        if photo4:
            supply.photo_4 = "/media/" + str(supply.photo_4)
        supply.save()

        return redirect('dashboard')  # Redirect to dashboard after submission

    return render(request, 'Supplies/add_supplies.html')

def delete_supplies(request, supply_id):
    slisting = get_object_or_404(SupplyListing, id=supply_id, user=request.user)

    slisting.delete()

    return redirect('dashboard')


def reviewSupply(request, listing_id):

    if request.method == 'POST':
        rating=request.POST.get('rating')
        review=request.POST.get('review')

        reviewObject = SupplyReview(
            rating = rating,
            description = review,
            user = request.user,
            listing_id = listing_id,
        )

        reviewObject.save()

    return redirect('dashboard')

def reviewHome(request, listing_id):
    
    if request.method == 'POST':
        rating=request.POST.get('rating')
        review=request.POST.get('review')

        reviewObject = HomeReview(
            rating = rating,
            description = review,
            user = request.user,
            listing_id = listing_id,
        )

        reviewObject.save()

    return redirect('dashboard')

