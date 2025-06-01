import requests
import logging
from .constants import WIKIDATA_SPARQL_URL, USER_AGENT

logger = logging.getLogger(__name__)

class WikidataAPIClient:
    def __init__(self, base_url: str = WIKIDATA_SPARQL_URL, timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {'User-Agent': USER_AGENT}

    def _request(self, params: dict) -> dict:
        """
        Internal method to make a GET request to the base_url.
        """
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}. URL: {self.base_url}, Params: {params}")
            raise # Re-raise the exception to be handled by the caller

    def execute_sparql_query(self, query: str) -> dict:
        """
        Executes a SPARQL query against the Wikidata API.
        """
        params = {'query': query, 'format': 'json'}
        try:
            return self._request(params)
        except requests.exceptions.RequestException as e:
            # _request already logged the general API failure.
            # Log specific context about the SPARQL query failure here.
            logger.error(f"SPARQL query execution failed. Query snippet: {query[:200]}... Error: {e}")
            raise # Re-raise the original RequestException

    def create_heritage_sparql_query(self, heritage_id: str, offset: int = 0, limit: int = 1000) -> str:
        """
        Generates a SPARQL query to retrieve heritage data from Wikidata.
        """
        return f"""SELECT DISTINCT ?itemLabel
                (SAMPLE(?image_) AS ?image)
                (GROUP_CONCAT(DISTINCT ?instanceOfTypeLabel_; SEPARATOR="; ") AS ?instanceOfTypeLabel)
                ?location ?inception
                (GROUP_CONCAT(DISTINCT ?adminEntityLabel_; SEPARATOR="; ") AS ?adminEntityLabel)
                ?historicCountyLabel
            WHERE {{
                SERVICE bd:slice {{
                    ?item wdt:P1435 wd:{heritage_id}.
                    bd:serviceParam bd:slice.offset {offset}.
                    bd:serviceParam bd:slice.limit {limit}.
                }}
                ?item wdt:P18 ?image_.
                ?item wdt:P31 ?instanceOfType.
                ?item wdt:P625 ?location.
                OPTIONAL {{ ?item wdt:P571 ?inception. }}
                OPTIONAL {{ ?item wdt:P131 ?adminEntity. }}
                OPTIONAL {{ ?item wdt:P7959 ?historicCounty. }}

                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".
                    ?item rdfs:label ?itemLabel.
                    ?instanceOfType rdfs:label ?instanceOfTypeLabel_.
                    ?adminEntity rdfs:label ?adminEntityLabel_.
                    ?historicCounty rdfs:label ?historicCountyLabel.
                }}
            }}
            GROUP BY ?itemLabel ?location ?inception ?historicCountyLabel"""