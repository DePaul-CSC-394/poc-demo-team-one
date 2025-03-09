from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Accounts.models import Profile
from Roommates.models import RoommateResponses

def roommates(request):
    return render(request, 'Roommates/roommate.html')  

def roommatesDashboard(request):
    users = User.objects.all()
    roommates = Profile.objects.filter(user__in=users)
    return render(request, 'Roommates/roommatesDashboard.html', {'roommates': roommates})

@login_required
def questionnaire_view(request):
    """
    Displays the roommate questionnaire and saves responses in RoommateResponses model.
    """
    if request.method == "POST":
        user = request.user
        roommate_responses, created = RoommateResponses.objects.get_or_create(user=user)

        roommate_responses.owns_pets = request.POST.get("owns_pets") == "Yes"
        roommate_responses.okay_with_pets = request.POST.get("okay_with_pets") == "Yes"
        roommate_responses.okay_with_female = request.POST.get("okay_with_female") == "Yes"
        roommate_responses.okay_with_male = request.POST.get("okay_with_male") == "Yes"
        roommate_responses.cleanliness = request.POST.get("cleanliness") == "Yes"
        roommate_responses.work_study = request.POST.get("work_study") == "Yes"
        roommate_responses.quiet_night = request.POST.get("quiet_night") == "Yes"
        roommate_responses.host_gatherings = request.POST.get("host_gatherings") == "Yes"
        roommate_responses.share_supplies = request.POST.get("share_supplies") == "Yes"

        roommate_responses.save()


        return redirect("roomatesDashboard")  # Redirect to profile page after submission

    return render(request, "roommates.html")
