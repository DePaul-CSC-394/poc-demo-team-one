import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Housing.models import HousingListing, HousingBooking
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random

class Command(BaseCommand):
    help = 'Populates the HousingListing and HousingBooking models with data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing the data')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        # Get or create a user to associate with the listings
        user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'password': 'admin'})

        with open(json_file_path, 'r') as file:
            data = json.load(file)  # Parse the entire file as a JSON array
            for item in data:
                try:
                    properties = item['properties']
                    geometry = item['geometry']

                    # Create a HousingListing instance
                    listing=HousingListing.objects.create(
                        user=user,
                        latitude=geometry['coordinates'][1],  # latitude
                        longitude=geometry['coordinates'][0],  # longitude
                        bedrooms=0,  # Default value, update as needed
                        bathrooms=1.0,  # Default value, update as needed
                        price=0.0,  # Default value, update as needed
                        sqFeet=0.0,  # Default value, update as needed
                        description=f"Address: {properties['number']} {properties['street']}",  
                    )

                    start_date=datetime.now() + timedelta(days=random.randint(1,30)) + relativedelta(months=random.randint(0,3))
                    end_date=start_date + timedelta(days=random.randint(1,14)) + relativedelta(months=random.randint(1,4))

                    HousingBooking.objects.create(
                        user=user,
                        listing=listing,
                        start_date=start_date,
                        end_date=end_date
                    )

                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"Missing key in JSON: {e}"))

        self.stdout.write(self.style.SUCCESS('Successfully populated HousingListing and HousingBooking data'))