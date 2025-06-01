import logging
from django.core.management.base import BaseCommand
from django.db.models import Count, Min
from myapp.models import Submission, Monument
from .process_data.remove import remove_duplicates, remove_unlinked
from .process_data.populate import populate_field

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Removes duplicate submission and monument entries with the same label and image_author'

    def handle(self, *args, **kwargs):
        # remove_duplicates(Submission)
        # logger.info('Duplicate submissions removal process completed.')
        # self.stdout.write(self.style.SUCCESS('Successfully removed duplicate submissions'))

        # remove_duplicates(Monument)
        # logger.info('Duplicate monuments removal process completed.')
        # self.stdout.write(self.style.SUCCESS('Successfully removed duplicate monuments'))

        # remove_unlinked()
        # logger.info('Unlinked monuments removal process completed.')
        # self.stdout.write(self.style.SUCCESS('Successfully removed unlinked monuments'))

        populate_field()
        logger.info('Field population process completed.')
        self.stdout.write(self.style.SUCCESS('Successfully populated fields'))