from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login as django_login
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # https://docs.djangoproject.com/en/5.1/topics/auth/default/

        user = authenticate(request, username=username, password=password)

        if user:
            django_login(request, user)
            return redirect('listings')
        else:
            #error
            context = {"error_msg" : "Invalid email or password."}
            return render(request, 'Accounts/login.html', context)
    return render(request, 'Accounts/login.html')

def signup(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm-password')

        #all fields are required
        if not username or not password or not confirmPassword:
            context = {"error_msg" : "Please enter all fields"}
            return render(request, 'Accounts/signup.html', context)
        
        #passwords must match
        if password != confirmPassword:
            context = {"error_msg" : "Passwords do not match"}
            return render(request, 'Accounts/signup.html', context)
        
        #username must be unique
        if User.objects.filter(username=username).exists():
            context = {"error_msg" : "Username already exists"}
            return render(request, 'Accounts/signup.html', context)
        
        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Account Created!")
        return redirect("login")

    return render(request, 'Accounts/signup.html')

def signout(request):
    logout(request)
    return redirect('login')

def profile(request):

    context = {
        "profile" : request.user.profile,
        "user" : request.user
    }

    return render(request, 'Accounts/profile.html', context)

def saveProfile(request):
    if request.method == "POST":

        photo = request.FILES.get('profile_image')

        profile = request.user.profile
        user = request.user
        profile.name = request.POST['name']
        profile.address_line1 = request.POST['address_line1']
        profile.address_line2 = request.POST['address_line2']
        profile.city = request.POST['city']
        profile.state = request.POST['state']
        profile.emergency_name = request.POST['city']
        profile.emergency_phone = request.POST['state']
        user.email = request.POST['email']
        profile.phone = request.POST['phone']
        profile.intro = request.POST['intro']
        profile.looking_roomate = 'looking' in request.POST
        profile.image = photo if photo else None

        profile.save()
        user.save()
        
        profile.image = "/media/" + str(profile.image)

        profile.save()
        user.save()

        context = {
            "profile" : request.user.profile,
            "user" : request.user
        }

        return render(request, 'Accounts/profile.html', context)