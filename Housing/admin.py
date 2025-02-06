from django.contrib import admin

from .models import HousingListing

# Register your models here.

class HousingListingAdmin(admin.ModelAdmin):
    list_display=('id', 'latitude', 'longitude')

admin.site.register(HousingListing, HousingListingAdmin);