from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Shows the database URL'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        if 'sqlite' in db_settings['ENGINE']:
            self.stdout.write(self.style.SUCCESS(f"Database URL: {db_settings['NAME']}"))
        else:
            url = f"{db_settings['ENGINE']}://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
            self.stdout.write(self.style.SUCCESS(f"Database URL: {url}"))