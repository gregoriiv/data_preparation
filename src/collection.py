"""This module contains all functions for the OSM data collection
with the Pyrosm package."""
import os
import time
import yaml
import subprocess
from pathlib import Path
from pyrosm import get_data, OSM
import pandas as pd
import numpy as np
import geopandas as gpd
from other.utility_functions import gdf_conversion
from config.config import Config
from db.db import DATABASE, Database
from fusion import database_table2df

# Function for collection data from OSM dbf and conversion to Dataframe
# Could be extended with varios type of searches and filters
# name - should be referenced to set from YAML file (e.g. "pois")
# pbf_region=None - when "None" data comes from YAML file, when specified - from it
# driver=None default variables driver could be (driver from "Fiona" drivers, e.g "GeoJSON", "GPKG")
# !! Notice if driver is specified it creates GeoJSON, but function still returns DF.
# !! If it is not specified func returns only DF

def pois_collection(conf=None,database=None, filename=None, return_type=None):
    if not conf:
        conf = Config('pois')
    else:
        print("Specify configuration!")
    if not database:
        database = DATABASE

    dbname, host, username, port, password = DATABASE['dbname'], DATABASE['host'], DATABASE['user'], DATABASE['port'], DATABASE['password']
    region_links = conf.collection_regions()
    work_dir = os.getcwd()
    os.chdir('src/data/input') 
    for i, rl in enumerate(region_links):
        subprocess.run(f'wget --no-check-certificate --output-document="pois-osm.osm.pbf" {rl}', shell=True, check=True)
        if i == 0:
            subprocess.run('cp pois-osm.osm.pbf pois-merged-osm.osm.pbf', shell=True, check=True)
        else:
            subprocess.run('osmosis --read-pbf pois-merged-osm.osm.pbf --read-pbf pois-osm.osm.pbf --merge --write-pbf pois-merged-osm-new.osm.pbf', shell=True, check=True)
            subprocess.run('rm pois-merged-osm.osm.pbf | mv pois-merged-osm-new.osm.pbf pois-merged-osm.osm.pbf', shell=True, check=True)
        
        subprocess.run('rm pois-osm.osm.pbf', shell=True, check=True)

    subprocess.run('osmosis --read-pbf file="pois-merged-osm.osm.pbf" --write-xml file="pois-merged_osm.osm"', shell=True, check=True)
    subprocess.run('osmconvert pois-merged_osm.osm --drop-author --drop-version --out-osm -o=pois-merged_osm_reduced.osm', shell=True, check=True)
    subprocess.run('rm pois-merged_osm.osm | mv pois-merged_osm_reduced.osm pois-merged_osm.osm', shell=True, check=True)
    subprocess.run('rm pois-merged-osm.osm.pbf', shell=True, check=True)
    obj_filter = conf.osm_object_filter()
    subprocess.run(obj_filter, shell=True, check=True)
    os.chdir(work_dir)
    conf.osm2pgsql_create_style()
    print(os.getcwd())
    subprocess.run(f'osm2pgsql -d {dbname} -H {host} -U {username} --port {port} --hstore -E 4326 -W -r .osm -c src/data/input/pois_collection.osm -s --drop -C 24000 --style src/config/pois_p4b.style --prefix osm_pois', shell=True, check=True)
    os.chdir('src/data/input')
    subprocess.run('rm pois-merged_osm.osm', shell=True, check=True)
    subprocess.run('rm pois_collection.osm', shell=True, check=True)
    os.chdir(work_dir)

    tables = ['osm_pois_line', 'osm_pois_point', 'osm_pois_polygon', 'osm_pois_roads']

    db = Database()
    con = db.connect()
    df_result = gpd.GeoDataFrame()

    for tab in tables:
        query1 = f'ALTER TABLE {tab} ALTER COLUMN tags TYPE jsonb USING tags::jsonb;'
        db.perform(query1)
        df = database_table2df(con, tab, geometry_column='way')
        df_result = pd.concat([df_result,df], sort=False).reset_index(drop=True)
    
    df_result["osm_id"] = abs(df_result["osm_id"])

    return gdf_conversion(df_result, filename, return_type)


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



#============================================OUTDATED=============================================#
#=================================================================================================#

# def osm_collect_filter(config, pbf_region=None, driver=None, update=False):
#     # Timer
#     print(f"Collection and filtering {config.name} started...")
#     start_time = time.time()

#     # get region name desired pois types from yaml settings
#     if pbf_region:
#         pbf_data = pbf_region
#     else:
#         pbf_data = config.pbf_data

#     # Get defined data from Geofabrik
#     fp = get_data(pbf_data, update=update)
#     osm = OSM(fp)

#     # Create filter class with given parameters and create filter with class method
#     custom_filter = config.pyrosm_filter()

#     # Get Data from OSM with given filter ###custom_filter.tags_as_columns
#     # Additional filters can be applied (e.g. keep_nodes=False, keep_ways=True,keep_relations=True)
#     df = osm.get_data_by_custom_criteria(*custom_filter)

#     print(f"Collection and filtering took {time.time() - start_time} seconds ---")

#     return_name = config.name + '_' + pbf_data

#     # Return type if driver -> 'GeoJSON' write geojson file if driver -> 'PandasDF' return PandasDF
#     return gdf_conversion(df, return_name ,driver)

#==================== Temporary functions to convert bus_stops lines to polygons==================#
# # Bug FIX (Relazted ot POIs)
# def bus_stop_conversion(df):
#     # Timer
#     start_time = time.time()
#     print("Bus stops conversion has been started...")

# # Conversion lines back to polygons
#     df.at[df['geometry'].geom_type == "MultiLineString", 'geometry'] = df['geometry'].convex_hull

#     print(f"Conversion bus stops took {time.time() - start_time} seconds ---")
#     return df

# # Function for Concatination of bus stops with pois
# # Return dataframe and dataframe name as TUPLE or record GeoJSON as void
# # INPUT: DF(pois), DF(buses), DF(pois) name, ruturn_type ("df" or "GeoJSON"), return_filename for GeoJSON if not defined in "df_pois_name"
# def join_osm_pois_n_busstops(df_pois,  df_stops, df_pois_name=None, return_type=None, return_filename = 'pois_merged'):
#     start_time = time.time()
#     print("Merging process of pois and bus_stops has been started...")
#     df = pd.concat([df_pois,df_stops],sort=False).reset_index(drop=True)
#     df = df.replace({np.nan: None})
#     print(f"Merging process of pois and bus_stops took {time.time() - start_time} seconds ---")
#     if df_pois_name:
#         return_name = df_pois_name
#     else:
#         return_name = return_filename

#     return gdf_conversion(df, return_name ,return_type)


# Function for pyrosm library
# def pois_collection(config=None,config_buses=None,update=False,filename=None,return_type=None):
#     df_res = pd.DataFrame()
#     if not config:
#         config = Config("pois")
#     if not config_buses:
#         config_buses = Config("bus_stops")
        
#     data_set = config.pbf_data

#     for d in data_set:
#         pois_collection = osm_collect_filter(config, d, update=update)
#         temp_df = join_osm_pois_n_busstops(pois_collection[0],
#                                                     bus_stop_conversion(osm_collect_filter(config_buses,d)[0]),
#                                                     pois_collection[1])
#         if data_set.index(d) == 0:
#             df_res = temp_df
#         else:
#             df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

#     return gdf_conversion(df_res, filename, return_type=return_type)
