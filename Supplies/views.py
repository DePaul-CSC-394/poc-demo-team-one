from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from .models import SupplyBooking, SupplyListing
import folium

# Create your views here.

def detail (request, listing_id):

    listing = get_object_or_404(SupplyListing, pk=listing_id)

    center_lat = listing.latitude  + Decimal(0.007)
    center_lon = listing.longitude - Decimal(0.007)

    #from documentation: https://python-visualization.github.io/folium/latest/user_guide.html
    # Create the map object
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, zoom_control=False, scrollWheelZoom=False, tiles="openstreetmap", dragging=False, doubleClickZoom=False)

    # Add markers (optional, for specific locations)
    # folium.Marker([listing.latitude, listing.longitude], popup="Location Name").add_to(m)
    radius = 100
    folium.CircleMarker(
        location=[center_lat, center_lon],
        radius=radius,
        color="cornflowerblue",
        fill=True,
        fill_opacity=0.6,
        opacity=1,
    ).add_to(m)

    # Get the HTML representation of the map
    map_html = m._repr_html_()



    context = {
        'listing' : listing,
        'map_html': map_html,
    }

    return render(request, 'Supplies/listing_details.html', context)