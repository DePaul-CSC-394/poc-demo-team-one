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

def add_listing(request):
    if request.method == 'POST':
        # Handle form submission
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        home_type = request.POST.get('homeType')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if photo1:
            default_storage.save(photo1.name, photo1)
        if photo2:
            default_storage.save(photo2.name, photo2)

        return render(request, 'Dashboard/dashboard.html')  # Redirect to dashboard after submission

    return render(request, 'Dashboard/add_listing.html')



def add_listing(request):
    if request.method == 'POST':
        # Handle form submission
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        home_type = request.POST.get('homeType')
        description = request.POST.get('description')
        price = request.POST.get('price')

        # Save files (example)
        if photo1:
            default_storage.save(photo1.name, photo1)
        if photo2:
            default_storage.save(photo2.name, photo2)

        # Redirect or process data further
        return render(request, 'Dashboard/dashboard.html')  # Redirect to dashboard after submission

    return render(request, 'Dashboard/add_listing.html')

