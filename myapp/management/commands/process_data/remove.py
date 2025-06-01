import logging
from django.db.models import Count, Min
from django.db.models import Exists, OuterRef
from myapp.models import Monument, Submission

logger = logging.getLogger(__name__)

def remove_duplicates(model):
    '''
    Removes duplicate submission and monument entries with the same label and image_author
    '''
    model_name = model.__name__
    logger.info(f"Starting duplicate removal for {model_name} based on 'label' and 'image_author'.")
    
    # Annotate with the count of duplicates and the minimum id
    duplicates = model.objects.values('label', 'image_author').annotate(
        dup_count=Count('id'),
        min_id=Min('id')
    ).filter(dup_count__gt=1)

    # Evaluate the queryset to get a list of duplicate groups to process
    # This avoids issues if the underlying data changes during iteration.
    duplicate_groups_to_process = list(duplicates)

    if not duplicate_groups_to_process:
        logger.info(f"No duplicate groups found for {model_name}.")
        return

    total_items_deleted_across_groups = 0
    for duplicate_group_info in duplicate_groups_to_process:
        label = duplicate_group_info['label']
        author = duplicate_group_info['image_author']
        min_id_to_keep = duplicate_group_info['min_id']

        logger.info(f"Processing duplicate group for {model_name}: label='{label}', image_author='{author}'. Keeping id={min_id_to_keep}.")
        
        # Exclude the item with the min_id and delete the rest
        delete_queryset = model.objects.filter(
            label=label,
            image_author=author
        ).exclude(
            id=min_id_to_keep
        )
        
        deleted_count_this_group, _ = delete_queryset.delete()
        if deleted_count_this_group > 0:
            logger.info(f"Deleted {deleted_count_this_group} duplicate entries for {model_name} (label='{label}', image_author='{author}').")
            total_items_deleted_across_groups += deleted_count_this_group
        else:
            logger.info(f"No entries to delete for this group (label='{label}', image_author='{author}') after excluding min_id (id={min_id_to_keep}).")
            
    logger.info(f"Finished duplicate removal for {model_name}. Total duplicates deleted: {total_items_deleted_across_groups}.")

def remove_unlinked():
    '''
    Removes heritage entries (Monuments) without an associated submission
    '''
    logger.info(f"Starting removal of unlinked {Monument.__name__} entries.")
    # Find all Monuments that do not have a matching Submission based on image_author
    monuments_to_delete_qs = Monument.objects.annotate(
        has_submission=Exists(
            Submission.objects.filter(
                image_author=OuterRef('image_author')
            )
        )
    ).filter(has_submission=False)

    initial_count_to_delete = monuments_to_delete_qs.count()
    logger.info(f"Found {initial_count_to_delete} {Monument.__name__} entries initially marked for deletion (no submission by same image_author).")

    if initial_count_to_delete == 0:
        logger.info(f"No unlinked {Monument.__name__} entries to delete.")
        return

    # Deleting the found monuments in batches
    batch_size = 100  # Define an appropriate batch size
    total_deleted_accumulator = 0

    while monuments_to_delete_qs.exists(): # QuerySet is re-evaluated here
        # Delete a batch of monuments
        # Slicing and then calling values_list executes the query for the batch
        ids_in_batch = list(monuments_to_delete_qs[:batch_size].values_list('id', flat=True))

        if not ids_in_batch: # Safety break, though .exists() should prevent this
            logger.warning("Exited unlinked monument deletion loop unexpectedly: no IDs in batch despite .exists() being true.")
            break

        num_deleted_this_batch, _ = Monument.objects.filter(id__in=ids_in_batch).delete()
        total_deleted_accumulator += num_deleted_this_batch
        logger.info(f"Deleted batch of {num_deleted_this_batch} {Monument.__name__} entries. "
                    f"Total deleted so far: {total_deleted_accumulator}/{initial_count_to_delete}.")

    logger.info(f"Finished processing unlinked {Monument.__name__} entries. "
                f"Initial count was {initial_count_to_delete}, actual total deleted: {total_deleted_accumulator}.")