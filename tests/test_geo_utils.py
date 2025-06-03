import pytest
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
from myapp.management.commands.process_data import _get_country

@pytest.fixture
def mock_gdf(monkeypatch):
    # Create a mock GeoDataFrame with a simple polygon
    from shapely.geometry import Polygon

    poly = Polygon([(-2, 51), (-2, 52), (0, 52), (0, 51)])
    df = gpd.GeoDataFrame({
        'CTYUA22NM': ['England'],
        'geometry': [poly]
    }, geometry='geometry')

    # Patch the global `gdf` in the geo_utils module
    monkeypatch.setattr("myapp.geo_utils.gdf", df)
    return df

def test_get_country_inside_polygon(mock_gdf):
    # Point inside the mock polygon
    latitude = 51.5
    longitude = -1.0
    country = _get_country(latitude, longitude)
    assert country == "England"

def test_get_country_outside_polygon(mock_gdf):
    # Point outside the mock polygon
    latitude = 55.0
    longitude = -4.0
    country = _get_country(latitude, longitude)
    assert country is None  # since the point isn't in the polygon