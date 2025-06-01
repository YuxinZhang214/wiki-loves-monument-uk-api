from django.core.management.base import BaseCommand
from myapp.models import Monument

class Command(BaseCommand):
    help = 'Deletes all records in the Monument table'

    def handle(self, *args, **kwargs):
        # This will delete all records in the Monument table
        Monument.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all Monument records'))