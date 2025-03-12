def calculate_match_score(responses1, responses2):
    """
    Calculates a match score between two users based only on their RoommateResponses.
    """

    base_score = 50

    weights = {
        "owns_pets": 5,
        "cleanliness": 16,
        "work_study": 9,
        "quiet_night": 14,
        "host_gatherings": 7,
        "share_supplies": 9
    }

    if (responses1.owns_pets and not responses2.okay_with_pets)  or (responses2.owns_pets and not responses1.okay_with_pets):
        return 0
    
    if (responses1.user.profile.gender=="female" and not responses2.okay_with_female)  or (responses2.user.profile.gender=="female" and not responses1.okay_with_female):
        return 0
    
    if (responses1.user.profile.gender=="male" and not responses2.okay_with_male)  or (responses2.user.profile.gender=="male" and not responses1.okay_with_male):
        return 0

    for key, weight in weights.items():
        if getattr(responses1, key) == getattr(responses2, key):
            base_score += weight
        else:
            base_score -= weight

    # if responses1.okay_with_pets is False and responses2.owns_pets is True:
    #     return 0
    # if responses2.okay_with_pets is False and responses1.owns_pets is True:
    #     return 0

    # if (responses1.okay_with_female is False and responses2.user.profile.gender == "female") or \
    #    (responses1.okay_with_male is False and responses2.user.profile.gender == "male"):
    #     return 0

    return max(0, min(100, base_score))
