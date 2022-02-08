import os
import sys
import yaml
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from other.utility_functions import gdf_conversion, file2df
from config.config import Config
from network.network_collection import network_collection
from network.ways import PrepareLayers


from collection import pois_collection, osm_collect_filter, gdf_conversion, bus_stop_conversion, join_osm_pois_n_busstops
from preparation import landuse_preparation, pois_preparation_region, buildings_preparation, school_categorization,kindergarten_deaggrgation

# from fusion import database_connection, fusion_data_areas_rs_set
from fusion import replace_data_area, database_connection, database_table2df, area_n_buffer2df, df2area, df2database, fuse_data_area, pois_fusion
from db.db import Database


# POIS Collection + Preparation + Fusion
 
##============================================================POIs Collection=============================================================================##

df = pois_collection(filename="pois_germany_collected",return_type="GeoJSON")[0]

##OUTDATED##
#osm_collect_filter(config, pbf_region="Oberbayern", driver="GeoJSON", update=False)

##============================================================POIs Preparation==========================================================##

df = pois_preparation_region(df,filename="pois_germany_prepared", return_type="GeoJSON")[0]

# # NOT DEFAULT
# # Convert pois_bayern file to remote DB (necessary to update layer manually then)
# df = file2df("pois_bayern.geojson")
# df2database(df,data_name)

##OUTDATED##
# df = pois_preparation_set(config, config_buses, update=False, filename=data_name, return_type="GeoJSON")[0]

#==============================================================POIs Fusion===========================================================================##
# ======  Fusion with config settings ====== #

#df = file2df("pois_bayern_prepared.geojson")
df = pois_fusion(df ,None, "pois_bayern_fused", "GeoJSON")

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
##======================= Network Collection and Preparation ==============================##
#network_collection()
# prep_layers = PrepareLayers('ways')
# prep_layers.ways()





##============================================TESTS==============================================##







#==============================================================CHECK===============================================================================##
