from django.core.management.base import BaseCommand
from django.db.models import Count, Min
from myapp.models import Submission, Monument

class Command(BaseCommand):
    help = 'Removes duplicate submission and monument entries with the same label and image_author'

    def remove_duplicates(self, model):
        # Annotate with the count of duplicates and the minimum id
        duplicates = model.objects.values('label', 'image_author').annotate(
            dup_count=Count('id'),
            min_id=Min('id')
        ).filter(dup_count__gt=1)

        for duplicate in duplicates:
            # Exclude the item with the min_id and delete the rest
            model.objects.filter(
                label=duplicate['label'], 
                image_author=duplicate['image_author']
            ).exclude(
                id=duplicate['min_id']
            ).delete()

    def handle(self, *args, **kwargs):
        self.remove_duplicates(Submission)
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate submissions'))

        self.remove_duplicates(Monument)
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate monuments'))