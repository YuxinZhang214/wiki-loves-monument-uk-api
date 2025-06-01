import os
import logging
import requests
from django.core.management.base import CommandError
from django.conf import settings

from myapp.service.wikidata import WikidataAPIClient
from myapp.service.wikimedia import WikimediaAPIClient 
from myapp.service.csv import CSVWriter
from myapp.service.csv import CSV_HEADERS as MONUMENT_CSV_HEADERS_CONFIG, parse_location as csv_parse_location

logger = logging.getLogger(__name__) 

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

def fetch_monuments_data():
    batch_size = 1000
    os.makedirs(DATA_DIRECTORY_MONUMENTS, exist_ok=True)
    wikidata_client = WikidataAPIClient()

    for heritage_id in MONUMENT_HERITAGE_IDS:
        logger.info(f"Processing monument heritage ID: {heritage_id}")
        offset = 0
        more_data = True
        
        csv_file_path = os.path.join(DATA_DIRECTORY_MONUMENTS, f'{heritage_id}.csv')
        csv_writer = CSVWriter(path=csv_file_path, custom_headers=MONUMENT_CSV_HEADERS_CONFIG)
        
        try:
            while more_data:
                logger.info(f"Fetching monument data for {heritage_id}, offset {offset}, limit {batch_size}...")
                query = WikidataAPIClient.create_heritage_sparql_query(heritage_id, offset, batch_size)
                try:
                    results = wikidata_client.execute_sparql_query(query)
                    bindings = results.get("results", {}).get("bindings", [])
                except requests.exceptions.RequestException as e:
                    logger.error(f"SPARQL query failed for monument {heritage_id}, offset {offset}: {e}")
                    more_data = False 
                    continue
                except CommandError as e: 
                    logger.error(f"SPARQL query command error for monument {heritage_id}, offset {offset}: {e}")
                    more_data = False
                    continue
                
                if not bindings:
                    logger.info(f"No more monument bindings found for {heritage_id} at offset {offset}.")
                    more_data = False
                    continue
                
                for result in bindings:
                    image_url = result.get("image", {}).get("value")
                    if not image_url:
                        logger.warning(f"No image URL for monument item: {result.get('itemLabel', {}).get('value', 'N/A')}")
                        continue

                    image_commons_data = WikimediaAPIClient.get_image_data(image_url)
                    
                    if image_commons_data:
                        author, submission_datetime_obj, submission_year, submission_date = image_commons_data
                        lon, lat = csv_parse_location(result.get("location", {}).get("value", ""))

                        row_data_dict = {
                            'Item Label': result.get("itemLabel", {}).get("value", "N/A"),
                            'Image': image_url,
                            'Author': author,
                            'Submission DateTime': submission_datetime_obj.isoformat() + 'Z' if submission_datetime_obj else "N/A",
                            'Year': submission_year,
                            'Date': submission_date,
                            'Instance Of Type Label': result.get("instanceOfTypeLabel", {}).get("value", "N/A"),
                            'Longitude': lon,
                            'Latitude': lat,
                            'Inception': result.get("inception", {}).get("value", "N/A"),
                            'Admin Entity Label': result.get("adminEntityLabel", {}).get("value", "N/A"),
                            'Historic County Label': result.get("historicCountyLabel", {}).get("value", "N/A"),
                        }
                        row_to_write = [row_data_dict.get(header) for header in MONUMENT_CSV_HEADERS_CONFIG]
                        csv_writer.write(row_to_write)
                
                offset += batch_size
        finally:
            csv_writer.close()
            
        logger.info(f"Finished processing and writing monument data for {heritage_id} to {csv_file_path}")
    logger.info("All monument heritage IDs processed successfully.")
