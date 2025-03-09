from Roommates.models import RoommateResponses

def calculate_match_score(user1, user2):
    """
    Calculates a match score between two users based only on their RoommateResponses.
    """

    base_score = 50
    responses1 = RoommateResponses.objects.get(user=user1)
    responses2 = RoommateResponses.objects.get(user=user2)

    weights = {
        "owns_pets": 15,
        "cleanliness": 10,
        "work_study": 10,
        "quiet_night": 10,
        "host_gatherings": 5,
        "share_supplies": 5
    }

    for key, weight in weights.items():
        if getattr(responses1, key) == getattr(responses2, key):
            base_score += weight
        else:
            base_score -= weight

    if responses1.okay_with_pets is False and responses2.owns_pets is True:
        return 0
    if responses2.okay_with_pets is False and responses1.owns_pets is True:
        return 0

    if (responses1.okay_with_female is False and responses2.user.profile.gender == "female") or \
       (responses1.okay_with_male is False and responses2.user.profile.gender == "male"):
        return 0

    return max(0, min(100, base_score))
