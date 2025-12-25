import csv
from django.core.management.base import BaseCommand
from api.models import fuelstation
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

class Command(BaseCommand):
    help = 'load fuel prices from csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='path to csv file')
        parser.add_argument('--no-geocode', action='store_true', help='skip geocoding')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        skip_geocode = options.get('no_geocode', False)
        
        geocoder = None
        geocode = None
        if not skip_geocode:
            geocoder = Nominatim(user_agent="us_route_app")
            geocode = RateLimiter(geocoder.geocode, min_delay_seconds=1)
        
        fuelstation.objects.all().delete()
        self.stdout.write('cleared existing fuel stations')
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            file.seek(0)
            
            delimiter = '\t' if '\t' in first_line else ','
            reader = csv.DictReader(file, delimiter=delimiter)
            stations = []
            count = 0
            
            for row in reader:
                try:
                    retail_price = float(row.get('Retail Price', 0))
                    if retail_price <= 0:
                        continue
                    
                    station = fuelstation(
                        opis_id=int(row.get('OPIS Truckstop ID', 0)),
                        name=row.get('Truckstop Name', '').strip(),
                        address=row.get('Address', '').strip(),
                        city=row.get('City', '').strip(),
                        state=row.get('State', '').strip(),
                        rack_id=int(row.get('Rack ID', 0)),
                        retail_price=retail_price
                    )
                    
                    if row.get('Latitude') and row.get('Longitude'):
                        try:
                            station.latitude = float(row.get('Latitude'))
                            station.longitude = float(row.get('Longitude'))
                            self.stdout.write(f'loaded with coords: {station.name}')
                        except:
                            pass
                    elif not skip_geocode and geocode:
                        full_address = f"{station.address}, {station.city}, {station.state}, USA"
                        try:
                            location = geocode(full_address)
                            if location:
                                station.latitude = location.latitude
                                station.longitude = location.longitude
                                self.stdout.write(f'geocoded: {station.name} - {station.city}')
                            else:
                                self.stdout.write(self.style.WARNING(f'no location: {full_address}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'geocoding error: {str(e)}'))
                    
                    stations.append(station)
                    count += 1
                    
                    if len(stations) >= 50:
                        fuelstation.objects.bulk_create(stations)
                        stations = []
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'error processing row: {str(e)}'))
            
            if stations:
                fuelstation.objects.bulk_create(stations)
            
            self.stdout.write(self.style.SUCCESS(f'loaded {count} fuel stations'))
