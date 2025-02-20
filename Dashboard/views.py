from django.shortcuts import get_object_or_404, render
from UniVerse import settings
from Housing.models import HousingListing, HousingBooking
from django.contrib.auth.models import User


# Create your views here.

def dashboard(request):
    # temp logic

    user = User.objects.get(username='admin') 
    request.user = user


    user=request.user

    if not user.is_authenticated:
        return render(request, 'Dashboard/dashboard.html')
        
    user_listings=HousingListing.objects.filter(user=user)

    for listing in user_listings:
        listing.pendings=list(
            HousingBooking.objects.filter(listing=listing, is_pending=True)
        )


    user_bookings=HousingBooking.objects.filter(user=user)

    return render(request, 'Dashboard/dashboard.html', {'user_listings': user_listings, 
        'user_bookings': user_bookings})



