import os
import csv
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
import requests
from urllib.parse import unquote

class Command(BaseCommand):
    help = 'Imports heritage data from Wikimedia Data and stores it in the database'

    def get_image_data(self,file_url):
        '''
        File information from wiki common
        '''
        # Extracting the file name from the URL
        file_name = unquote(file_url.split('/')[-1])

        # Wikimedia Commons API endpoint for fetching file information
        commons_api_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": f"File:{file_name}",
            "prop": "imageinfo",
            "iiprop": "user|timestamp|",
            "format": "json"
        }

        response = requests.get(commons_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            page = next(iter(data["query"]["pages"].values()))
            if "imageinfo" in page:
                imageinfo = page["imageinfo"][0]
                author = imageinfo.get('user')
                
                submission_datetime = datetime.strptime(imageinfo.get('timestamp'), '%Y-%m-%dT%H:%M:%SZ')
                submission_month = submission_datetime.month
                
                # Check if the submission month is September
                if submission_month == 9:
                    submission_year = submission_datetime.year
                    submission_date = submission_datetime.day
                
                    return author, submission_datetime, submission_year, submission_date
                else:
                    return None  # Indicate that this record should be skipped because it's not from September
                
        return None

    def parse_location(self, location_str):
        if location_str.startswith("Point(") and location_str.endswith(")"):
            coordinates_str = location_str[6:-1]
            longitude, latitude = coordinates_str.split()
            return float(longitude), float(latitude)
        return None, None

    def get_item(self, endpoint_url, query):
        '''
            Get wikidata item
        '''
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        headers = {'User-Agent': user_agent}
        params = {'query': query, 'format': 'json'}
        response = requests.get(endpoint_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

    def create_query(self, heritage_id, offset=0, limit=1000):
        return f"""
         SELECT DISTINCT ?itemLabel 
            (sample(?image_) as ?image) 
            (group_concat(distinct ?instanceOfTypeLabel_;separator="; " ) as ?instanceOfTypeLabel)  
            ?location 
            ?inception 
            (group_concat(distinct ?adminEntityLabel_;separator="; " ) as ?adminEntityLabel)  
            ?historicCountyLabel 
        WHERE {{
            SERVICE bd:slice {{
                ?item wdt:P1435 wd:{heritage_id}.
                bd:serviceParam bd:slice.offset {offset} .
                bd:serviceParam bd:slice.limit {limit} .
            }}
            ?item wdt:P18 ?image_.
            ?item wdt:P31 ?instanceOfType.
            ?item wdt:P625 ?location.
            OPTIONAL {{ ?item wdt:P571 ?inception . }}
            OPTIONAL {{ ?item wdt:P131 ?adminEntity . }}
            OPTIONAL {{ ?item wdt:P7959 ?historicCounty . }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". 
                        ?item rdfs:label ?itemLabel . 
                        ?instanceOfType rdfs:label ?instanceOfTypeLabel_ . 
                        ?adminEntity rdfs:label ?adminEntityLabel_ .
                        ?historicCounty rdfs:label ?historicCountyLabel .}}
        }} 
        GROUP BY ?itemLabel ?location ?inception ?historicCountyLabel
        """

    def handle(self, *args, **kwargs):
        # Example heritage IDs for demonstration. Replace or add as needed.
        heritage_ids = [
            "Q219538",  # Scheduled Monument

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
        
        batch_size = 1000
        
        # Loop over each heritage ID to create and process queries
        for heritage_id in heritage_ids:
            offset = 310000
            more_data = True  # Flag to continue fetching data in batches
            
            # Open the CSV file for writing once per heritage ID
            data_directory = './data/heritage'
            os.makedirs(data_directory, exist_ok=True)
            csv_file_path = os.path.join(data_directory, f'{heritage_id}.csv')
            
            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['Item Label', 'Image', 'Author', 'Submission DateTime', 'Year', 'Date', 'Instance Of Type Label', 'Longitude', 'Latitude', 'Inception', 'Admin Entity Label', 'Historic County Label'])
                
                while more_data:
                    query = self.create_query(heritage_id, offset)
                    results = self.get_item("https://query.wikidata.org/sparql", query)
                    bindings = results.get("results", {}).get("bindings", [])
                    print(f'fetching data {offset}')
                    
                    if not bindings:
                        more_data = False  # No more data to process, exit the loop
                        break
                    
                    for result in bindings:
                        image = result["image"]["value"]
                        image_data = self.get_image_data(image)
                        
                        # Process and write to CSV only if image_data is not None
                        if image_data:
                            author, submission_datetime, submission_year, submission_date = image_data
                            
                            itemLabel = result["itemLabel"]["value"]
                            instanceOfTypeLabel = result.get("instanceOfTypeLabel", {}).get("value", "N/A")
                            location_str = result.get("location", {}).get("value", "N/A")
                            inception = result.get("inception", {}).get("value", "N/A")
                            adminEntityLabel = result.get("adminEntityLabel", {}).get("value", "N/A")
                            historicCountyLabel = result.get("historicCountyLabel", {}).get("value", "N/A")
                            
                            # Extracting longitude and latitude
                            longitude, latitude = self.parse_location(location_str)
                            
                            # Writing data to the CSV
                            writer.writerow([itemLabel, image, author, submission_datetime, submission_year, submission_date, instanceOfTypeLabel, longitude, latitude, inception, adminEntityLabel, historicCountyLabel])
                    
                    offset += batch_size  # Prepare for the next batch
