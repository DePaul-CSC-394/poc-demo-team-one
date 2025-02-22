import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Housing.models import HousingListing, HousingBooking
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Populates the HousingListing and HousingBooking models with data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing the data')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        # Get or create a user to associate with the listings
        user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com'}
        )
        if created:
         user.set_password('admin')  # Hashes the password correctly
         user.save()


        
        # Get or create a user to associate with the listings
        renter, renterCreated = User.objects.get_or_create(
        username='renter',
        defaults={'email': 'renter@example.com'}
        )
        if renterCreated:
         renter.set_password('renter')  # Hashes the password correctly
         renter.save()


        with open(json_file_path, 'r') as file:
            data = json.load(file)  # Parse the entire file as a JSON array
            for item in data:
                try:
                    properties = item['properties']
                    geometry = item['geometry']
                    bookings = item.get('bookings',[])


                    # Create a HousingListing instance
                    listing=HousingListing.objects.create(
                        user=user,
                        latitude=geometry['coordinates'][1],  # latitude
                        longitude=geometry['coordinates'][0],  # longitude
                        bedrooms=0,  # Default value, update as needed
                        bathrooms=1.0,  # Default value, update as needed
                        price=0.0,  # Default value, update as needed
                        sqFeet=0.0,  # Default value, update as needed
                        home_type=properties['home_type'],
                        description=item['desc'],  
                        photo_1=item['photo1'],
                        photo_2=item['photo2'],
                    )


                    for booking in bookings:
                        HousingBooking.objects.create(
                        user=renter,
                        listing=listing,
                        start_date=make_aware(datetime.fromisoformat(booking["start_date"])),
                        end_date=make_aware(datetime.fromisoformat(booking["end_date"]))
                    )
                   


                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"Missing key in JSON: {e}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))



        self.stdout.write(self.style.SUCCESS('Successfully populated HousingListing and HousingBooking data'))


