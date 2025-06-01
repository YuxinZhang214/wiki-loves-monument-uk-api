# /Users/yuxinzhang/Github/wiki-loves-monument-uk-api/myapp/management/commands/fetch_data.py
import os
import logging
import requests # For requests.exceptions.RequestException
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings # Import Django settings

# Imports from service layer
from .fetch.monuments import fetch_monuments_data
from .fetch.submissions import fetch_submissions_data

# Specific CSV headers for monuments, and parse_location from csv service
from myapp.service.csv import CSV_HEADERS as MONUMENT_CSV_HEADERS_CONFIG, parse_location as csv_parse_location

logger = logging.getLogger(__name__)

# --- Constants for Monument Fetching ---
# Define paths relative to the project's BASE_DIR for robustness
DATA_DIRECTORY_MONUMENTS = os.path.join(settings.BASE_DIR, 'data', 'heritage')
MONUMENT_HERITAGE_IDS = [
    "Q219538",    # Scheduled Monument
    "Q15700818",  # Grade I Listed Building
    "Q15700831",  # Grade IIs Listed Building
    "Q15700834",  # Grade II Listed Building
    "Q10729054",  # category_A_listed_building
    "Q10729125",  # category_B_listed_building
    "Q10729142",  # category_C_listed_building
    "Q71055272",  # Grade_A_listed_building
    "Q71056106",  # Grade_B_listed_building
    "Q71056072",  # Grade_C_listed_building
]

# --- Constants for Submission Fetching ---
DATA_DIRECTORY_SUBMISSIONS = os.path.join(settings.BASE_DIR, 'data', 'submission')
SUBMISSION_YEARS = [2013, 2014, 2016, 2017, 2018, 2019, 2020, 2022, 2023]
SUBMISSION_FIELDNAMES = ['Item Label', 'Image', 'Author', 'Submission Date', 'Year', 'Date', 'Longitude', 'Latitude']

class Command(BaseCommand):
    help = 'Fetches heritage monument data and/or Wiki Loves Monuments image submissions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['monuments', 'submissions', 'all'],
            default='all',
            help='Specify the type of data to fetch: "monuments", "submissions", or "all". Default is "all".'
        )

    def handle(self, *args, **options):
        fetch_type = options['type']
        overall_success = True

        if fetch_type == 'monuments' or fetch_type == 'all':
            logger.info("Starting to fetch monument data...")
            try:
                fetch_monuments_data()
                logger.info("Successfully fetched monument data.")
            except Exception as e:
                logger.error(f"An error occurred during monument data fetching: {e}", exc_info=True)
                self.stderr.write(self.style.ERROR(f"Failed to fetch monument data: {e}"))
                overall_success = False

        if fetch_type == 'submissions' or fetch_type == 'all':
            logger.info("Starting to fetch submission data...")
            try:
                self._fetch_submissions_data()
                logger.info("Successfully fetched submission data.")
            except Exception as e:
                logger.error(f"An error occurred during submission data fetching: {e}", exc_info=True)
                self.stderr.write(self.style.ERROR(f"Failed to fetch submission data: {e}"))
                overall_success = False

        if overall_success:
            logger.info("Data fetching process completed successfully for selected type(s).")
            self.stdout.write(self.style.SUCCESS("Data fetching process completed successfully for selected type(s)."))
        else:
            logger.error("Data fetching process completed with errors.")
            # CommandError will indicate failure to the Django management command system
            raise CommandError("Data fetching process completed with one or more errors. Check logs.")
