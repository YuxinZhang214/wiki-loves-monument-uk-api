import csv
import logging
import os

from datetime import datetime
from dateutil import parser as date_parser
from django.core.management.base import BaseCommand
from myapp.models import Monument, Submission

logger = logging.getLogger(__name__)
    
def parse_inception_date(date_string):
    # Check if the date_string is "N/A" or any other non-date format string you expect
    if date_string.strip().upper() in ["N/A", ""]:
        return None  # Return None to indicate a null value should be used
    
    try:
        # Attempt to parse the date string including time part
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        # If the first format fails, try ISO format
        try:
            parsed_date = datetime.fromisoformat(date_string.rstrip('Z'))
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Failed to parse date from string: {date_string}. Error: {e}")
            return None
    
class Command(BaseCommand):
    help = 'Loads data from CSV files into the database for image submissions and heritage data'

    # No need for command arguments since directories are hardcoded
    def handle(self, *args, **kwargs):
        heritage_directory = 'data/heritage'
        submission_directory = 'data/submission'
        
        # Process heritage data
        self.process_files(heritage_directory, is_heritage=True)
        
        # Process submission data
        self.process_files(submission_directory, is_heritage=False)

    def process_files(self, directory, is_heritage):
        try:
            for filename in os.listdir(directory):
                csv_file_path = os.path.join(directory, filename)
                self.stdout.write(f'Processing file: {filename}')

                # Extract heritage_designation from the file name
                heritage_designation = os.path.splitext(filename)[0].replace('_', ' ')

                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        try:
                            if is_heritage:
                                item = self.transform_heritage_item(row, heritage_designation)
                                Monument.objects.create(**item)
                            else:
                                item = self.transform_submission_item(row)
                                Submission.objects.create(**item)
                        except ValueError as e:
                            logger.warning(f"Skipping row due to invalid data: {row}. Error: {e}")
                            continue

                    self.stdout.write(self.style.SUCCESS(f'Successfully populated the database from {filename}'))

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.stdout.write(self.style.ERROR('Failed to populate the database'))


    def transform_submission_item(self, item):
        # Convert empty strings for numeric fields to None
        longitude = item.get("Longitude", '').strip() or None
        latitude = item.get("Latitude", '').strip() or None
        if longitude is not None:
            try:
                longitude = float(longitude)
            except ValueError:
                logger.error(f"Invalid longitude '{longitude}' for item: {item['Item Label']}")
                longitude = None
        if latitude is not None:
            try:
                latitude = float(latitude)
            except ValueError:
                logger.error(f"Invalid latitude '{latitude}' for item: {item['Item Label']}")
                latitude = None

        return {
            'label': item.get("Item Label", ""),
            'image_url': item.get("Image", ""),
            'image_author': item.get("Author", ""),
            'longitude': longitude,
            'latitude': latitude,
            'year': item.get("Year", ""), 
            'date': item.get("Date", "")
        }

    def transform_heritage_item(self, item, heritage_designation):
        # Convert empty strings for numeric fields to None
        longitude = item.get("Longitude", '').strip() or None
        latitude = item.get("Latitude", '').strip() or None
        if longitude is not None:
            try:
                longitude = float(longitude)
            except ValueError:
                logger.error(f"Invalid longitude '{longitude}' for item: {item['Item Label']}")
                longitude = None
        if latitude is not None:
            try:
                latitude = float(latitude)
            except ValueError:
                logger.error(f"Invalid latitude '{latitude}' for item: {item['Item Label']}")
                latitude = None

        return {
            'label': item.get("Item Label", ""),
            'image_url': item.get("Image", ""),
            'image_author': item.get("Author", ""),
            'year': item.get("Year", ""), 
            'date': item.get("Date", ""),
            'instance_of_type_label': item.get("Instance Of Type Label", ""),
            'longitude': longitude,
            'latitude': latitude,
            'inception': parse_inception_date(item.get("Inception", "")),
            'admin_entity_label': item.get("Admin Entity Label", ""),
            'historic_county_label': item.get("Historic County Label", ""),
            'heritage_designation': heritage_designation,
        }