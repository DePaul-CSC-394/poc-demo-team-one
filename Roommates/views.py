from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Accounts.models import Profile
from Roommates.models import RoommateResponses
from .matching import calculate_match_score 
from django.core.cache import cache

def roommates(request):

    userResponse = RoommateResponses.objects.filter(user=request.user).first()

    if not userResponse:
        return render(request, 'Roommates/roommate.html') 

    cache_key=f"sorted_matches_{request.user.id}_{userResponse.updated_at.timestamp()}"

    cached_matches=cache.get(cache_key)

    sortedMatches= cached_matches
    return render(request, 'Roommates/roommatesDashboard.html', {'roommates': sortedMatches})

@login_required
def editResponses(request):
    
    roommate_responses = RoommateResponses.objects.filter(user=request.user).first()

    return render(request, 'Roommates/roommate.html', {'roommate_responses': roommate_responses})

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

def refreshResults(request):
    userResponse = get_object_or_404(RoommateResponses, user=request.user)
    cache_key=f"sorted_matches_{request.user.id}_{userResponse.updated_at.timestamp()}"

    
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
    roommate_responses, created = RoommateResponses.objects.get_or_create(user=request.user)

    if request.method == "POST":
        
        def clean_input(value_list):
            if isinstance(value_list, list) and len(value_list) > 0:
                return value_list[0] == "Yes"  
            return False  

        roommate_responses.owns_pets = clean_input(request.POST.getlist("owns_pets"))
        roommate_responses.okay_with_pets = clean_input(request.POST.getlist("okay_with_pets"))
        roommate_responses.okay_with_female = clean_input(request.POST.getlist("okay_with_female"))
        roommate_responses.okay_with_male = clean_input(request.POST.getlist("okay_with_male"))
        roommate_responses.cleanliness = clean_input(request.POST.getlist("cleanliness"))
        roommate_responses.work_study = clean_input(request.POST.getlist("work_study"))
        roommate_responses.quiet_night = clean_input(request.POST.getlist("quiet_night"))
        roommate_responses.host_gatherings = clean_input(request.POST.getlist("host_gatherings"))
        roommate_responses.share_supplies = clean_input(request.POST.getlist("share_supplies"))

        roommate_responses.save()
        return redirect("roommatesDashboard") 

    return render(request, "Roommates/roommate.html", {"roommate_responses": roommate_responses})

