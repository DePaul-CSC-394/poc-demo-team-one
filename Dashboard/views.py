from django.shortcuts import get_object_or_404, render
from UniVerse import settings
from Housing.models import HousingListing, HousingBooking


# Create your views here.

def dashboard(request):
    # listings = HousingListing.objects.all()
    user=request.user

    if not user.is_authenticated:
        return render(request, 'Dashboard/dashboard.html')
        
    user_listings=HousingListing.objects.filter(user=user)

    user_bookings=HousingBooking.objects.filter(user=user)

    return render(request, 'Dashboard/dashboard.html', {'user_listings': user_listings, 'user_bookings': user_bookings})



