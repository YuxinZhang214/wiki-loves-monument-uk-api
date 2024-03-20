from datetime import datetime
import requests
import os
import csv
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Fetches detailed Wiki Loves Monuments image submissions for specific years'

    def get_title(self, canonicaltitle):
        '''
            Extract file name between 'File:' and '.jpg' (or other extensions)
        '''
        return canonicaltitle.split(':', 1)[-1].rsplit('.', 1)[0]

    def get_image_details(self, titles):
        details_url = 'https://commons.wikimedia.org/w/api.php'
        titles_str = '|'.join(titles)  # Join titles with | for the API request
        params = {
            'action': 'query',
            'prop': 'imageinfo',
            'titles': titles_str,
            'iiprop': 'user|timestamp|url|extmetadata',
            'format': 'json'
        }
        response = requests.get(details_url, params=params).json()

        details_list = []
        for _, page in response['query']['pages'].items():
            if 'imageinfo' in page:
                imageinfo = page['imageinfo'][0]
                title = self.get_title(page.get('title'))
                author = imageinfo.get('user')
                
                # Parse the timestamp and split into year and date
                submission_datetime = datetime.strptime(imageinfo.get('timestamp'), '%Y-%m-%dT%H:%M:%SZ')
                submission_year = submission_datetime.year
                submission_date = submission_datetime.day
                
                image_url = imageinfo['url']
                
                longitude = imageinfo['extmetadata'].get('GPSLongitude', {}).get('value') if 'extmetadata' in imageinfo else None
                latitude = imageinfo['extmetadata'].get('GPSLatitude', {}).get('value') if 'extmetadata' in imageinfo else None
                
                details_list.append({
                    'Item Label': title,
                    'Image': image_url,
                    'Author': author,
                    'Submission Date': submission_datetime,
                    'Year': submission_year,
                    'Date': submission_date,
                    'Longitude': longitude,
                    'Latitude': latitude
                })
        return details_list

    def handle(self, *args, **options):
        years = [2013, 2014, 2016, 2017, 2018, 2019, 2020, 2022, 2023]
        for year in years:
            self.stdout.write(f'Fetching submissions for {year}...')
            base_url = 'https://commons.wikimedia.org/w/api.php'
            category = f"Images_from_Wiki_Loves_Monuments_{year}_in_the_United_Kingdom"
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': f'Category:{category}',
                'cmtype': 'file',
                'cmlimit': '50',  # Fetch up to 50 images per batch
                'format': 'json'
            }

            continue_param = {}
            data_dir = './data/submission/'
            file_path = os.path.join(data_dir, f"{year}.csv")
            
            with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Item Label', 'Image', 'Author', 'Submission Date', 'Year', 'Date', 'Longitude', 'Latitude']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if os.stat(file_path).st_size == 0:  # Check if file is empty to write header
                    writer.writeheader()

                while True:
                    response = requests.get(base_url, params={**params, **continue_param}).json()
                    if response.get('error'):
                        raise CommandError(f"API Error: {response.get('error').get('info')}")

                    images = response.get('query', {}).get('categorymembers', [])
                    titles = [image['title'] for image in images]
            
                    if titles:
                        image_details_list = self.get_image_details(titles)
                        for image_details in image_details_list:
                            writer.writerow(image_details)

                    if 'continue' in response:
                        continue_param = response['continue']
                    else:
                        break

            self.stdout.write(self.style.SUCCESS(f'Successfully fetched and saved detailed submissions for {year}'))

        self.stdout.write(self.style.SUCCESS('Completed fetching all specified years.'))