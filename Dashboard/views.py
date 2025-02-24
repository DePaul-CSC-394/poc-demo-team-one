from django.shortcuts import get_object_or_404, render, redirect
from UniVerse import settings
from Housing.models import HousingListing, HousingBooking
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


    user_bookings=HousingBooking.objects.filter(user=user)

    return render(request, 'Dashboard/dashboard.html', {'user_listings': user_listings, 
        'user_bookings': user_bookings})

def add_listing(request):
    if request.method == 'POST':
        # Handle form submission
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        # full_name = request.POST.get('fullName')
        # email = request.POST.get('email')
        # phone = request.POST.get('phone')
        home_type = request.POST.get('homeType')
        address = request.POST.get('address')
        bedrooms = request.POST.get('bedrooms')
        bathrooms = request.POST.get('bathrooms')
        sqFeet = request.POST.get('sqFeet')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if photo1:
            default_storage.save(photo1.name, photo1)
        if photo2:
            default_storage.save(photo2.name, photo2)

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
            photo_1=photo1,
            photo_2=photo2,
            # full_name=full_name,
            # email=email,
            # phone=phone,
            home_type=home_type,
            latitude=latitude,
            longitude=longitude,
            # address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            sqFeet=sqFeet,
            description=description,
            price=price
        )

        listing.save()

        return redirect('dashboard')  # Redirect to dashboard after submission

    return render(request, 'Dashboard/add_listing.html')

def approve_or_deny (request):
    if request.method == 'POST':
        booking_id=request.POST.get('booking_id')
        action=request.POST.get('action')

        booking = get_object_or_404(HousingBooking, id=booking_id)
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
            booking.was_denied=False
            subject="Your Booking Has Been Denied"
            message=f"Dear {booking.user.username}, \n\n Unfortuneatly, your booking has been denied."

        
        booking.save()

        send_mail(
            subject,
            message,
            'UniVerse@example.com',
            [user_email],
            fail_silently=TRUE
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