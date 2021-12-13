#%%
import os
import sys
import yaml
#import paramiko
import pandas as pd
import geopandas as gpd

from collection import Config, osm_collect_filter, gdf_conversion, bus_stop_conversion, join_osm_pois_n_busstops
from preparation import file2df, landuse_preparation, pois_preparation

#from fusion import geonode_connection, fusion_data_areas_rs_set
from fusion import replace_data_area, geonode_connection, geonode_table2df, area_n_buffer2df, df2area, df2geonode, fuse_data_area
#from credidentials_geonode import serv_password, db_password
from db.db import Database

# POIS Collection + Preparation

data_set = ["Mittelfranken","Niederbayern","Oberbayern","Oberfranken","Oberpfalz","Schwaben","Unterfranken"]

config = Config("pois")
config_buses = Config("bus_stops")

##===================================Collection POIs=============================================##

# # 1st way - Create separate files for each region in list

# for d in data_set:
#     pois_collection = osm_collect_filter(config,d,update=False)
#     pois_bus_collection = join_osm_pois_n_busstops(pois_collection[0],bus_stop_conversion(osm_collect_filter(config_buses,d)[0]),pois_collection[1])

#     pois_preparation(dataframe=pois_bus_collection[0], config=config, return_type="GPKG",result_name=pois_bus_collection[1])

# #========================================================##

# 2nd way - Download it separately and merge it together in one file k
# Return type 'GPKG' could be used

# data_name = "pois_bayern"

# df_res = pd.DataFrame()

# for d in data_set:
#     pois_collection = osm_collect_filter(config,d, update=False)
#     pois_bus_collection = join_osm_pois_n_busstops(pois_collection[0],
#                                                    bus_stop_conversion(osm_collect_filter(config_buses,d)[0]),
#                                                    pois_collection[1])
#     temp_df = pois_preparation(dataframe=pois_bus_collection[0], config=config, result_name=pois_bus_collection[1])[0]
#     if data_set.index(d) == 0:
#         df_res = temp_df
#     else:
#         df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

# df = gdf_conversion(df_res, data_name, return_type='GPKG')[0]

# df = file2df("pois_bayern.gpkg")

# df2geonode(df,data_name)

#==============================================================Fusion POIs===========================================================================##
# ======  Fusion with config settings ======

con = geonode_connection()

table_base = config.fusion["table_base"]
rs_set = config.fusion["rs_set"]
typen = ["geonode","geojson"]

df_base = geonode_table2df(con, table_base, geometry_column="geom")
df_area = area_n_buffer2df(con, rs_set, buffer=8300)
df_base2area = df2area(df_base, df_area)

for typ in typen:
    fusion_key_set = config.fusion_key_set(typ)

    for key in fusion_key_set:
        print(key)
        fusion_set = config.fusion_set(typ,key)
        if typ == 'geojson':
            filename = key + '.' + typ
            df_input = file2df(filename)
        elif typ == 'geonode':
            df_input = geonode_table2df(con, key)
        df_input2area = df2area(df_input, df_area)
        
        if config.fusion_type(typ, key) == "fuse":
            df_base2area = fuse_data_area(df_base2area, df_area, df_input, *fusion_set, return_name = None, return_type=None)[0]
        elif config.fusion_type(typ, key) == "replace":
            df_base2area = replace_data_area(df_base2area, df_area, df_input, *fusion_set[:-1], return_name = None, return_type=None)[0]
        else:
            print("Fusion type for %s was not defined. Fusion was not done." % key)
            pass

gdf_conversion(df_base2area, "fusion_pois_test", return_type='GPKG')

##============================================================== Landuse Collection + Preparation + Export to GeoNode ===============================================================================##

# config = Config("landuse")
# df_res = pd.DataFrame()

# for d in data_set:
#     landuse_collection = osm_collect_filter(config,d, update=True)

#     temp_df = landuse_preparation(dataframe=landuse_collection[0],result_name=landuse_collection[1], config=config)[0]
#     if data_set.index(d) == 0:
#         df_res = temp_df
#     else:
#         df_res = pd.concat([df_res,temp_df],sort=False).reset_index(drop=True)

# df = gdf_conversion(df_res, "landuse_bayern", return_type=None)[0]


# df.to_postgis(con=Database().connect_sqlalchemy(), name="landuse_bayern",if_exists='replace')

##==============================================================TESTS===============================================================================##
# %%
