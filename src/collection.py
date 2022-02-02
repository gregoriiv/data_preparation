"""This module contains all functions for the OSM data collection
with the Pyrosm package."""
import time
import yaml
from pathlib import Path
from pyrosm import get_data, OSM
import pandas as pd
import numpy as np
from other.utility_functions import gdf_conversion
from config.config import Config

# Function for collection data from OSM dbf and conversion to GeoJSON
# Could be extended with varios type of searches and filters
# name - should be referenced to set from YAML file (e.g. "pois")
# pbf_region=None - when "None" data comes from YAML file, when specified - from it
# driver=None default variables driver could be (driver from "Fiona" drivers, e.g "GeoJSON", "GPKG")
# !! Notice if driver is specified it creates GeoJSON, but function still returns DF.
# !! If it is not specified func returns only DF
# update=True parameter to download fresh data from OSM

def osm_collect_filter(config, pbf_region=None, driver=None, update=False):
    # Timer
    print(f"Collection and filtering {config.name} started...")
    start_time = time.time()

    # get region name desired pois types from yaml settings
    if pbf_region:
        pbf_data = pbf_region
    else:
        pbf_data = config.pbf_data

    # Get defined data from Geofabrik
    fp = get_data(pbf_data, update=update)
    osm = OSM(fp)

    # Create filter class with given parameters and create filter with class method
    custom_filter = config.pyrosm_filter()

    # Get Data from OSM with given filter ###custom_filter.tags_as_columns
    # Additional filters can be applied (e.g. keep_nodes=False, keep_ways=True,keep_relations=True)
    df = osm.get_data_by_custom_criteria(*custom_filter)

    print(f"Collection and filtering took {time.time() - start_time} seconds ---")

    return_name = config.name + '_' + pbf_data

    # Return type if driver -> 'GeoJSON' write geojson file if driver -> 'PandasDF' return PandasDF
    return gdf_conversion(df, return_name ,driver)

#==================== Temporary functions to convert bus_stops lines to polygons==================#
# Bug FIX (Relazted ot POIs)
def bus_stop_conversion(df):
    # Timer
    start_time = time.time()
    print("Bus stops conversion has been started...")

# Conversion lines back to polygons
    df.at[df['geometry'].geom_type == "MultiLineString", 'geometry'] = df['geometry'].convex_hull

    print(f"Conversion bus stops took {time.time() - start_time} seconds ---")
    return df

# Function for Concatination of bus stops with pois
# Return dataframe and dataframe name as TUPLE or record GeoJSON as void
# INPUT: DF(pois), DF(buses), DF(pois) name, ruturn_type ("df" or "GeoJSON"), return_filename for GeoJSON if not defined in "df_pois_name"
def join_osm_pois_n_busstops(df_pois,  df_stops, df_pois_name=None, return_type=None, return_filename = 'pois_merged'):
    start_time = time.time()
    print("Merging process of pois and bus_stops has been started...")
    df = pd.concat([df_pois,df_stops],sort=False).reset_index(drop=True)
    df = df.replace({np.nan: None})
    print(f"Merging process of pois and bus_stops took {time.time() - start_time} seconds ---")
    if df_pois_name:
        return_name = df_pois_name
    else:
        return_name = return_filename

    return gdf_conversion(df, return_name ,return_type)

def pois_collection(config=None,config_buses=None,update=False,filename=None,return_type=None):
    df_res = pd.DataFrame()
    if not config:
        config = Config("pois")
    if not config_buses:
        config_buses = Config("bus_stops")
        
    data_set = config.pbf_data

    for d in data_set:
        pois_collection = osm_collect_filter(config, d, update=update)
        temp_df = join_osm_pois_n_busstops(pois_collection[0],
                                                    bus_stop_conversion(osm_collect_filter(config_buses,d)[0]),
                                                    pois_collection[1])
        if data_set.index(d) == 0:
            df_res = temp_df
        else:
            df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

    return gdf_conversion(df_res, filename, return_type=return_type)


#======================================== Buildings collection ===================================#

def osm_collect_buildings(name='buildings', driver=None):
    #import data from pois_coll_conf.yaml
    with open(Path(__file__).parent/'config/config.yaml', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    var = config['VARIABLES_SET']

    # get region name desired pois types from yaml settings
    pbf_data = var['region_pbf']
    # query_values = var[name]['query_values']
    # filter = var[name]['tags']['filter']
    # additional = var[name]['tags']['additional']
    # point = var[name]['points']
    # polygon = var[name]['polygons']
    # line = var[name]['lines']

    # Get defined data from Geofabrik
    fp = get_data(pbf_data)
    osm = OSM(fp)

    buildings = osm.get_buildings()

    return gdf_conversion(buildings, name, return_type=driver)

