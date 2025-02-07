from django.shortcuts import render

# Create your views here.

def listings(request):
    return render(request, 'Housing/listings.html')