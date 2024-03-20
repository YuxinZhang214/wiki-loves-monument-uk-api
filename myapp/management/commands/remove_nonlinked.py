from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from myapp.models import Monument, Submission

class Command(BaseCommand):
    help = 'Removes heritage entries without an associated submission'

    def handle(self, *args, **kwargs):
        # Find all Monuments that do not have a matching Submission based on image_author
        monuments_without_submission = Monument.objects.annotate(
            has_submission=Exists(
                Submission.objects.filter(
                    image_author=OuterRef('image_author')
                )
            )
        ).filter(has_submission=False)
        
        # Count of monuments to be deleted for logging
        total_count = monuments_without_submission.count()
        self.stdout.write(f"Total monuments to delete: {total_count}")

        # Deleting the found monuments in batches
        batch_size = 100  # Define an appropriate batch size
        deleted_count = 0
        
        while monuments_without_submission.exists():
            # Delete a batch of monuments
            ids_to_delete = monuments_without_submission[:batch_size].values_list('id', flat=True)
            Monument.objects.filter(id__in=list(ids_to_delete)).delete()
            
            deleted_count += len(ids_to_delete)
            self.stdout.write(f"Deleted {deleted_count}/{total_count} monuments...")

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted all monuments without associated submissions.'))