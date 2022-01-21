import os
import sys
import yaml
#import paramiko
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

from collection import Config, osm_collect_filter, gdf_conversion, bus_stop_conversion, join_osm_pois_n_busstops
from preparation import file2df, landuse_preparation, pois_preparation, buildings_preparation, school_categorization,pois_preparation_set,kindergarten_deaggrgation

# from fusion import database_connection, fusion_data_areas_rs_set
from fusion import replace_data_area, database_connection, database_table2df, area_n_buffer2df, df2area, df2database, fuse_data_area, fusion_set
from db.db import Database

# POIS Collection + Preparation

# data_set = ["Mittelfranken","Niederbayern","Oberbayern","Oberfranken","Oberpfalz","Schwaben",\
#             "Unterfranken"]
data_set = ["Mittelfranken"]

config = Config("pois")
config_buses = Config("bus_stops")

##============================================================Collection + Preparation POIs==========================================================##

#osm_collect_filter(config, pbf_region="Oberbayern", driver="GeoJSON", update=False)


data_name = "pois_bayern"

# df = pois_preparation_set(config, config_buses, update=False, filename=data_name, return_type="GeoJSON")[0]

# # Convert pois_bayern file to remote DB (necessary to update layer manually then)
# df = file2df("pois_bayern.geojson")
# df2database(df,data_name)

#==============================================================Fusion POIs===========================================================================##
# ======  Fusion with config settings ====== #

# df = fusion_set(config, "pois_prepared_goat", return_type="GeoJSON")

# df = file2df("pois_prepared_goat.geojson")
# df2database(df,"pois_prepared_goat")

##==============================================================School preparation===================================================================##

# table_school = "jedeschule_geocode"
# sc_df = database_table2df(con, table_school, geometry_column="geom")
# school_categorization(sc_df, config, table_school, "GeoJSON")

# df = file2df("childcare_bayern.geojson")
# kindergarten_deaggrgation(df, "childcare_bayern_de", "GeoJSON")

##======================= Landuse Collection + Preparation + Export to Remote DB ==================##

# config = Config("landuse")
# df_res = pd.DataFrame()
# data_set = config.region_pbf

# for d in data_set:
#     landuse_collection = osm_collect_filter(config,d, update=True)

#     temp_df = landuse_preparation(dataframe=landuse_collection[0],result_name=landuse_collection[1], config=config)[0]
#     if data_set.index(d) == 0:
#         df_res = temp_df
#     else:
#         df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

# df = gdf_conversion(df_res, "landuse_bayern", return_type=None)[0]


#df.to_postgis(con=Database().connect_sqlalchemy(), name="landuse_bayern",if_exists='replace')

##======================= Buildings Collection + Export to Remote DB ==============================##

# config = Config("buildings")
# df_res = pd.DataFrame()

# for d in data_set:
#     buildings_collection = osm_collect_filter(config,d, update=True)

#     temp_df = buildings_preparation(dataframe=buildings_collection[0],result_name=buildings_collection[1], config=config)[0]
#     if data_set.index(d) == 0:
#         df_res = temp_df
#     else:
#         df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

# df = gdf_conversion(df_res, "buildings_osm_bavaria", return_type=None)[0]

#!!!nicht vergessen DB.yaml zu verändern von localhost zu Remote DB!!!!
# df.to_postgis(con=Database().connect_sqlalchemy(), name="landuse_bayern",if_exists='replace')

##============================================TESTS==============================================##

#==============================================================CHECK===============================================================================##
