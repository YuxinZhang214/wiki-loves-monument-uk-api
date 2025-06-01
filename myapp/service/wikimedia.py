import requests
from datetime import datetime
from urllib.parse import unquote
import logging
import sys

logger = logging.getLogger(__name__)

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT_FORMAT = "WLM-UK-API-Fetcher/1.0 (Python/{}.{}; " \
                    "https://github.com/yuxinzhang/wiki-loves-monument-uk-api; " \
                    "wlm-uk-bot@example.com)"

class WikimediaAPIClient:
    def __init__(self, base_url=COMMONS_API_URL, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.user_agent = USER_AGENT_FORMAT.format(sys.version_info[0], sys.version_info[1])
        self.headers = {'User-Agent': self.user_agent}

    def get_image_list(self, params):
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}. URL: {self.base_url}, Params: {params}")
            raise # Re-raise the exception to be handled by the caller

    def get_image_data(self,file_url: str) -> tuple[str, datetime, int, int] | None:
        '''
        Fetches file information from Wikimedia Commons.
        '''
        # Extracting the file name from the URL
        file_name = unquote(file_url.split('/')[-1])
        params = {
            "action": "query",
            "titles": f"File:{file_name.replace('_', ' ')}", # API often expects spaces for titles
            "prop": "imageinfo",
            "iiprop": "user|timestamp", 
            "format": "json"
        }
        try:
            user_agent = USER_AGENT_FORMAT.format(sys.version_info[0], sys.version_info[1])
            headers = {'User-Agent': user_agent}
            response = requests.get(COMMONS_API_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            data = response.json()

            if not data.get("query") or not data["query"].get("pages"):
                logger.warning(f"No pages found in API response for File:{file_name}")
                return None

            # Check for missing page or -1 pageid (invalid title)
            page_id = list(data["query"]["pages"].keys())[0]
            if page_id == "-1":
                logger.warning(f"Invalid title or missing page for File:{file_name}")
                return None

            page = data["query"]["pages"][page_id]
            if "imageinfo" in page and page["imageinfo"]: # Check if imageinfo is not empty
                imageinfo = page["imageinfo"][0]
                author = imageinfo.get('user')
                timestamp_str = imageinfo.get('timestamp')
                if not author or not timestamp_str:
                    logger.warning(f"Missing author or timestamp for File:{file_name}")
                    return None

                submission_datetime = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
                # Check if the submission month is September (Wiki Loves Monuments contest month)
                if submission_datetime.month == 9:
                    return author, submission_datetime, submission_datetime.year, submission_datetime.day
                else:
                    logger.debug(f"Skipping {file_name}, not submitted in September.")
                    return None # Not in September
            else:
                logger.warning(f"No imageinfo found for File:{file_name}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image data for {file_name}: {e}")
        except (KeyError, ValueError, IndexError) as e: # Catch potential errors during JSON parsing or data extraction
            logger.error(f"Error processing image data for {file_name}: {e}")
        return None

def parse_location(location_str: str) -> tuple[float, float] | tuple[None, None]:
    """
    Parses a location string in the format "Point(longitude latitude)"
    into a tuple of (longitude, latitude).
    Returns (None, None) if parsing fails.
    """
    if location_str.startswith("Point(") and location_str.endswith(")"):
        coordinates_str = location_str[6:-1]
        try:
            longitude, latitude = map(float, coordinates_str.split())
            return longitude, latitude
        except ValueError:
            logger.warning(f"Could not parse coordinates from location string: {location_str}")
    return None, None