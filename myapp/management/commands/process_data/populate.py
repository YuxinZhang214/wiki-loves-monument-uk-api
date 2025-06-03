import logging
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from myapp.models import Monument, Submission

logger = logging.getLogger(__name__)

# Load shapefile
shapefile_path = "./myapp/management/commands/process_data/geo_data/CTRY_DEC_2024_UK_BFC.shp"
gdf = gpd.read_file(shapefile_path)
# Ensure CRS match
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

def populate_field():
    '''
    Populates country fields for each Monument and Submission with progress updates.
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
        if i % 100 == 0 or i == total:
            logger.info(f'Processed {i}/{total} {object_type} objects...')

def _update_country(obj):
    country = _get_country(obj.latitude, obj.longitude)
    if country:
        obj.country = country
        obj.save(update_fields=['country'])

def _get_country(latitude, longitude):
    if latitude is None or longitude is None:
        logger.warning("Latitude or longitude is None. Skipping country fetch")
        return None
    # Correct: shapely Point expects (longitude, latitude)
    point = Point(longitude, latitude) 

    # Create GeoSeries from point for spatial query
    matched_row = gdf[gdf.contains(point)]

    if not matched_row.empty:
        name = matched_row.iloc[0]['CTRY24NM']  # Adjust column name if different
        return name
    else:
        logger.warning(f"No match found in shapefile for point: {point}")
        return None