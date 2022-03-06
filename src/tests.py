import os
import sys
import yaml
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from other.utility_functions import gdf_conversion, file2df, df2database, df2rdatabase,database_table2df
from config.config import Config
#from network.network_collection import network_collection
from network.ways import PrepareLayers


from collection import osm_collection,gdf_conversion
from preparation import landuse_preparation, pois_preparation, buildings_preparation, school_categorization,kindergarten_deaggrgation

# from fusion import database_connection, fusion_data_areas_rs_set
from fusion import replace_data_area, database_table2df, area_n_buffer2df, df2area, fuse_data_area, pois_fusion
from db.db import Database


# POIS Collection + Preparation + Fusion
 
##============================================================POIs Collection=============================================================================##

#df = osm_collection('pois',None, filename="pois_docker_test_collected",return_type="GeoJSON")[0]
# db = Database()
# con = db.connect()
# pois = database_table2df(con, 'pois_bayern_fused', geometry_column='geom')



##OUTDATED##
#osm_collect_filter(config, pbf_region="Oberbayern", driver="GeoJSON", update=False)

##============================================================POIs Preparation==========================================================##
# df = file2df("pois_docker_test_collected.geojson")
# df = pois_preparation(df, filename="pois_docker_test_prepared", return_type="GeoJSON")[0]
# df2rdatabase(df, 'pois_bayern_goat')
# df2database(df, 'pois_bayern')


# # NOT DEFAULT -- takes file cd app
# # Convert pois_bayern file to remote DB (necessary to update layer manually then)
# df = file2df("pois_bayern.geojson")
# df2database(df,data_name)

##OUTDATED##
# df = pois_preparation_set(config, config_buses, update=False, filename=data_name, return_type="GeoJSON")[0]

#==============================================================POIs Fusion===========================================================================##
# ======  Fusion with config settings ====== #
# df = file2df("pois_docker_test_prepared.geojson")
# df = osm_collection('pois')[0]
# df = pois_preparation(df, None, "pois_prepared", "GeoJSON")[0]
#df = pois_fusion(df ,None, "pois_cut_id_tests", "GeoJSON")

##==============================================================School preparation===================================================================##

# table_school = "jedeschule_geocode"
# sc_df = database_table2df(con, table_school, geometry_column="geom")
# school_categorization(sc_df, config, table_school, "GeoJSON")

# df = file2df("childcare_bayern.geojson")
# kindergarten_deaggrgation(df, "childcare_bayern_de", "GeoJSON")

##======================= Landuse Collection + Preparation + Export to Remote DB ==================##

# df = osm_collection('landuse', None, 'osm_landuse_collection', 'GeoJSON')[0]

# df = file2df('osm_landuse_collection.geojson')

# df = landuse_preparation(df, None, 'landuse_prepared', 'GeoJSON')[0]

##======================= Buildings Collection + Export to Remote DB ==============================##

# df = osm_collection('buildings',None, 'buildings_osm_collected', 'GPKG')[0]

# df = file2df('test_build.gpkg')
# df = buildings_preparation(df,None,filename='buildings_osm_prepared',return_type='GPKG')



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
print(os.getcwd())
prep_layers = PrepareLayers('ways')
prep_layers.ways()





##============================================TESTS==============================================##



#==============================================================CHECK===============================================================================##
