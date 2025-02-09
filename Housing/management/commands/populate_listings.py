import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Housing.models import HousingListing  
class Command(BaseCommand):
    help = 'Populates the HousingListing model with data from a JSON Lines file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON Lines file containing the data')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        # Get or create a user to associate with the listings
        user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'password': 'admin'})

        with open(json_file_path, 'r') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())  # Parse each line as a JSON object
                    properties = data['properties']
                    geometry = data['geometry']

                    # Create a HousingListing instance
                    HousingListing.objects.create(
                        user=user,
                        latitude=geometry['coordinates'][1],  # latitude
                        longitude=geometry['coordinates'][0],  # longitude
                        bedrooms=0,  # Default value, update as needed
                        bathrooms=1.0,  # Default value, update as needed
                        price=0.0,  # Default value, update as needed
                        sqFeet=0.0,  # Default value, update as needed
                        description=f"Address: {properties['number']} {properties['street']}",  # Custom description
                    )
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f"Error decoding JSON: {e}"))
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"Missing key in JSON: {e}"))

        self.stdout.write(self.style.SUCCESS('Successfully populated HousingListing data'))