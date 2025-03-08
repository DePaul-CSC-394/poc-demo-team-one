from django.shortcuts import render

def roommates(request):
    return render(request, 'Roommates/roommate.html')  # Ensure this template exists
