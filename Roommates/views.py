from django.shortcuts import render
from django.contrib.auth.models import User
from Accounts.models import Profile

def roommates(request):
    return render(request, 'Roommates/roommate.html')  

def roommatesDashboard(request):
    users = User.objects.all()
    roommates = Profile.objects.filter(user__in=users)
    return render(request, 'Roommates/roommatesDashboard.html', {'roommates': roommates})
