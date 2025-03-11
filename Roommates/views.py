from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Accounts.models import Profile
from Roommates.models import RoommateResponses
from .matching import calculate_match_score 
from django.core.cache import cache

def roommates(request):
    return render(request, 'Roommates/roommate.html')  

def roommatesDashboard(request):
    userResponse = get_object_or_404(RoommateResponses, user=request.user)
    cache_key=f"sorted_matches_{request.user.id}_{userResponse.updated_at.timestamp()}"

    cached_matches=cache.get(cache_key)

    if cached_matches:
        sortedMatches= cached_matches
    else:     
    
    # roommates = Profile.objects.all()

        responses = RoommateResponses.objects.all()

        results = dict() 

        for response in responses:
            if response.user != request.user:
                score = calculate_match_score(userResponse, response)
                if score!=0:
                    results.update({response.user.profile : score})
    
        sortedMatches = sorted(results.items(), key=lambda score: score[1], reverse=True)

        cache.set(cache_key, sortedMatches, timeout=3600)

    return render(request, 'Roommates/roommatesDashboard.html', {'roommates': sortedMatches})

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


        return redirect("roommatesDashboard")  # Redirect to Roomate Dashboard page after submission

    return render(request, "Roomates/roommates.html")
