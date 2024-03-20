import requests
from django.core.management.base import BaseCommand
from myapp.models import Monument, Submission

class Command(BaseCommand):
    help = 'Populates country fields for each Monument and Submission with progress updates.'

    def handle(self, *args, **kwargs):
        # Update Monument objects
        self.update_objects(Monument.objects.all(), 'Monument')
        # Update Submission objects
        self.update_objects(Submission.objects.all(), 'Submission')

        self.stdout.write(self.style.SUCCESS('Successfully updated country fields for Monuments and Submissions.'))

    def update_objects(self, objects, object_type):
        total = objects.count()
        self.stdout.write(f'Updating country for {total} {object_type} objects...')
        
        # for i, obj in enumerate(objects, start=1):
        #     self.update_country(obj)
        #     if i % 100 == 0 or i == total:  # Print progress every 100 items or on last item
        #         self.stdout.write(f'Processed {i}/{total} {object_type} objects...')

    def update_country(self, obj):
        country = self.get_country(obj.latitude, obj.longitude)
        if country:
            obj.country = self.standardize_country_name(country)
            obj.save(update_fields=['country'])

    def get_country(self, latitude, longitude):
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&zoom=3"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            return data.get('address', {}).get('state', None)
        return None
    
    def standardize_country_name(self, name):
        replacements = {
            "Cymru / Wales": "Wales",
            "Northern Ireland / Tuaisceart Éireann": "Northern Ireland",
            "Alba / Scotland": "Scotland"
        }
        return replacements.get(name, name)