import csv
import os

CSV_HEADERS = ['Item Label', 'Image', 'Author', 'Submission DateTime', 'Year', 'Date',
               'Instance Of Type Label', 'Longitude', 'Latitude', 'Inception',
               'Admin Entity Label', 'Historic County Label']

class CSVWriter:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.file = open(path, mode='a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        if os.stat(self.path).st_size == 0:
            self.writer.writerow(CSV_HEADERS)

    def prepare_row(self, item, image_info):
        author, sub_dt, year, day = image_info
        return [
            item.get("itemLabel", {}).get("value", "N/A"),
            item.get("image", {}).get("value", "N/A"),
            author,
            sub_dt,
            year,
            day,
            item.get("instanceOfTypeLabel", {}).get("value", "N/A"),
            *parse_location(item.get("location", {}).get("value", "")),
            item.get("inception", {}).get("value", "N/A"),
            item.get("adminEntityLabel", {}).get("value", "N/A"),
            item.get("historicCountyLabel", {}).get("value", "N/A"),
        ]

    def write(self, row):
        self.writer.writerow(row)

    def close(self):
        self.file.close()

def parse_location(location_str):
    if location_str.startswith("Point("):
        lon, lat = location_str[6:-1].split()
        return float(lon), float(lat)
    return None, None