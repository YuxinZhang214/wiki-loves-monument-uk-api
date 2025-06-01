from datetime import datetime
import requests
import os
import logging
import csv
from django.conf import settings
from django.core.management.base import CommandError
from myapp.service.wikimedia import WikimediaAPIClient
from myapp.service.csv import CSVWriter
from myapp.service.csv import CSV_HEADERS as MONUMENT_CSV_HEADERS_CONFIG, parse_location as csv_parse_location

logger = logging.getLogger(__name__)

# --- Constants for Submission Fetching ---
DATA_DIRECTORY_SUBMISSIONS = os.path.join(settings.BASE_DIR, 'data', 'submission')
SUBMISSION_YEARS = [2013, 2014, 2016, 2017, 2018, 2019, 2020, 2022, 2023]
SUBMISSION_FIELDNAMES = ['Item Label', 'Image', 'Author', 'Submission Date', 'Year', 'Date', 'Longitude', 'Latitude']

def fetch_submissions_data(self):
    os.makedirs(DATA_DIRECTORY_SUBMISSIONS, exist_ok=True)
    for year in SUBMISSION_YEARS:
        file_path = os.path.join(DATA_DIRECTORY_SUBMISSIONS, f"{year}.csv")
        logger.info(f"Processing submissions for year: {year}, output to {file_path}")
        try:
            submissions = _fetch_submissions(year)
            if submissions:
                _write_submission_csv(file_path, submissions, SUBMISSION_FIELDNAMES)
                logger.info(f'Successfully fetched and saved detailed submissions for {year}')
            else:
                logger.info(f'No submission details found or fetched for {year}')
        except CommandError as e: 
            logger.error(f"Failed to process submissions for year {year}: {e}")
    
    logger.info('Completed fetching all specified submission years.')


def _fetch_submissions(year):
    """Fetches submissions for a given year from Wikimedia Commons."""
    logger.info(f'Fetching submissions for year {year}...')
    client = WikimediaAPIClient()
    category = f"Images_from_Wiki_Loves_Monuments_{year}_in_the_United_Kingdom"
    # Note: cmlimit can be up to 500 for bots/approved scripts, '50' is safer default.
    params = {
        'action': 'query', 'list': 'categorymembers',
        'cmtitle': f'Category:{category}', 'cmtype': 'file',
        'cmlimit': '500', 'format': 'json' 
    }
    all_details = []
    continue_param = {}
    while True:
        try:
            current_params = {**params, **continue_param}
            response = client.get_image_list(current_params)
            images = response.get('query', {}).get('categorymembers', [])
            titles = [image.get('title') for image in images if image.get('title')]

            if titles:
                image_details_list = _get_batch_image_details(titles, client=client)
                all_details.extend(image_details_list)

            if 'continue' in response:
                continue_param = response['continue']
            else:
                break
        except (requests.exceptions.RequestException, CommandError) as e:
            logger.error(f"Error fetching submissions for year {year} during API call: {e}")
            raise CommandError(f"Failed to fetch submissions for year {year}: {e}")
    return all_details

def _write_submission_csv(file_path, data, fieldnames):
    """Writes image submission details to a CSV file."""
    csv_writer = CSVWriter(path=file_path, custom_headers=fieldnames)
    for row_dict in data:
        row_to_write = [row_dict.get(fn) for fn in fieldnames]
        csv_writer.write(row_to_write)
    csv_writer.close()

def _get_batch_image_details(titles: list[str], client: WikimediaAPIClient = None) -> list[dict]:
    """
    Fetches detailed image information for a batch of titles from Wikimedia Commons,
    formatted for submissions.
    """
    if not titles:
        return []
        
    api_client = client or WikimediaAPIClient()
    titles_str = '|'.join(titles)
    params = {
        'action': 'query', 'prop': 'imageinfo', 'titles': titles_str,
        'iiprop': 'user|timestamp|url|extmetadata', 'format': 'json'
    }
    try:
        response_json = api_client.get(params)
        return _parse_batch_image_details(response_json)
    except requests.exceptions.RequestException as e:
        raise CommandError(f"Wikimedia API request failed during batch image details fetch: {e}")
    

def _parse_batch_image_details(api_response_json: dict) -> list[dict]:
    """Parses the Wikimedia Commons API batch response for image details for submissions."""
    details_list = []
    pages = api_response_json.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        if page_id == "-1" or "missing" in page_data:
            logger.warning(f"Page missing or invalid for ID {page_id}, title: {page_data.get('title')}")
            continue
        extracted_info = _extract_submission_image_info(page_data)
        if extracted_info:
            details_list.append(extracted_info)
    return details_list

def _extract_submission_image_info(page_data: dict) -> dict | None:
    """
    Extracts specific image details from a single page API response,
    formatted for submission data.
    """
    if 'imageinfo' not in page_data or not page_data['imageinfo']:
        logger.debug(f"No imageinfo found for page: {page_data.get('title', 'Unknown title')}")
        return None

    imageinfo = page_data['imageinfo'][0]
    
    item_label = _get_simple_title_from_canonical(page_data.get('title'))
    author = imageinfo.get('user')
    timestamp_str = imageinfo.get('timestamp')
    image_url = imageinfo.get('url')

    if not all([item_label, author, timestamp_str, image_url]):
        logger.warning(
            f"Missing essential data (label, author, timestamp, or URL) for page: {page_data.get('title')}. "
            f"Details - Label: {item_label}, Author: {author}, Timestamp: {timestamp_str}, URL: {image_url}"
        )
        return None

    try:
        submission_datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
        submission_year = submission_datetime_obj.year
        submission_day_of_month = submission_datetime_obj.day
    except ValueError:
        logger.error(f"Could not parse timestamp: {timestamp_str} for page: {page_data.get('title')}")
        return None

    extmetadata = imageinfo.get('extmetadata', {})
    longitude = extmetadata.get('GPSLongitude', {}).get('value')
    latitude = extmetadata.get('GPSLatitude', {}).get('value')

    return {
        'Item Label': item_label, 'Image': image_url, 'Author': author,
        'Submission Date': submission_datetime_obj.isoformat() + 'Z', # Standard ISO format
        'Year': submission_year, 'Date': submission_day_of_month,
        'Longitude': longitude, 'Latitude': latitude
    }

def _get_simple_title_from_canonical(canonical_title: str) -> str | None:
    """Extracts a simplified title from a canonical Wikimedia title (e.g., 'File:Name.jpg' -> 'Name')."""
    if not canonical_title:
        return None
    try:
        # Remove "File:" prefix and extension
        name_with_ext = canonical_title.split(':', 1)[-1]
        return name_with_ext.rsplit('.', 1)[0]
    except IndexError:
        logger.warning(f"Could not parse canonical title: {canonical_title}")
        return canonical_title # Fallback or return None