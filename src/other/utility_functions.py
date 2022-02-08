import os
import sys
import time
from pathlib import Path
import geopandas as gp

# Function for creation backupfiles
# Convert and save dataframe as GPKG or GeoJSON file formats
# Use it as return result for data preparation functions
def gdf_conversion(gdf, name=None, return_type=None):
    """can convert a GeoGataFrame(gdf) into GeoJSON or GPKG, but always returns the gdf and name"""
    if return_type == "GeoJSON":
        print(f"Writing down the geojson file {name + '.geojson'} ...")
        start_time = time.time()
        gdf.to_file(os.path.join('src', 'data', 'output',  (name +'.geojson')), driver=return_type)
        print(f"Writing file {time.time() - start_time} seconds ---")
        print(f"GeoJSON {name + '.geojson'} was written.")
        return gdf, name
    elif return_type == "GPKG":
        print(f"Writing down the geopackage file {name + '.gpkg'} ...")
        start_time = time.time()
        gdf.to_file(os.path.join('src', 'data', 'output', (name +'.gpkg')), driver=return_type)
        print(f"Writing file {time.time() - start_time} seconds ---")
        print(f"GeoPackage {name + '.gpkg'} was written.")
        return gdf, name
    else:
        return gdf, name

def file2df(filename):
    name, extens = filename.split(".")
    if extens == "geojson":
        file = open(os.path.join('src', 'data', 'input', filename), encoding="utf-8")
        df = gp.read_file(file)
    elif extens == "gpkg":
        file = os.path.join('src', 'data', 'input',filename)
        df = gp.read_file(file)
    else:
        print("Extension of file %s currently doen not support with file2df() function." % filename)
        sys.exit()
    return df     
    