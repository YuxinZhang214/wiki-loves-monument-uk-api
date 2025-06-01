import logging
import requests
from myapp.models import Monument, Submission

logger = logging.getLogger(__name__)

def populate_field():
    '''
    'Populates country fields for each Monument and Submission with progress updates.
    '''
    _update_objects(Monument.objects.all(), 'Monument')
    logger.info('Successfully updated country fields for Monuments.')
    
    _update_objects(Submission.objects.all(), 'Submission')
    logger.info('Successfully updated country fields for Submissions.')

def _update_objects(objects, object_type):
    total = objects.count()
    logger.info(f'Updating country for {total} {object_type} objects...')
    
    for i, obj in enumerate(objects, start=1):
        _update_country(obj)
        if i % 100 == 0 or i == total:  # Print progress every 100 items or on last item
            logger.info(f'Processed {i}/{total} {object_type} objects...')

def _update_country(obj):
    country = _get_country(obj.latitude, obj.longitude)
    if country:
        obj.country = _standardize_country_name(country)
        obj.save(update_fields=['country'])

def _get_country(latitude, longitude):
    if latitude is None or longitude is None:
        logger.warning(f"Latitude or longitude is None. Skipping country fetch. Lat: {latitude}, Lon: {longitude}")
        return None
    # zoom level 5 to get detailed regional subdivisions within the UK
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&zoom=5"
    try:
        response = requests.get(url, headers={'User-Agent': 'WLMUKAPI/1.0 PopulateCountry'}, timeout=10)
        response.raise_for_status() 
        data = response.json()

        country_name = data.get('address', {}).get('state')
        if not country_name:
            logger.warning(f"Could not determine country/state from Nominatim response for lat={latitude}, lon={longitude}. Response: {data.get('address')}")
        return country_name
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching country for lat={latitude}, lon={longitude} from {url}: {e}")
        return None
    except ValueError as e: # Includes JSONDecodeError
        logger.error(f"Error decoding JSON response for lat={latitude}, lon={longitude} from {url}: {e}")
        return None

def _standardize_country_name(name):
    replacements = {
        "Cymru / Wales": "Wales",
        "Northern Ireland / Tuaisceart Éireann": "Northern Ireland",
        "Alba / Scotland": "Scotland"
    }
    return replacements.get(name, name)