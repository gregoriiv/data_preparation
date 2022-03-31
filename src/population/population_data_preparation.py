import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from src.other.utility_functions import migrate_all_tables2localdb, drop_table, df2database
from src.collection import osm_collection
from src.network.network_collection import network_collection
from src.network.ways import PrepareLayers
from src.preparation import landuse_preparation
from src.export.export_goat import getDataFromSql
from src.config.config import Config
from src.config.osm_dict import gms_keys

def population_data_preparation(municipalities):

    # Preparation of additional layers: 'landuse', 'landuse_additional', 'buildings_custom', 'census', 'study_area', 'building_osm', 'landuse_osm', 'ways', 'pois', 'planet_osm_point'
    layers = ['landuse', 'landuse_additional', 'buildings_custom', 'census', 'study_area', 'building_osm', 'landuse_osm', 'ways', 'pois', 'planet_osm_point']
    getDataFromSql(layers, municipalities)
    migrate_all_tables2localdb()


# population_data_preparation(['083110000','091620000'])


#     # landuse_osm preparation from rs mun codes
#     new_pbf_data = []
#     for mun in municipalities:
#         bks = mun[0:2]
#         if bks in ['09', '08', '05']:
#             bks = mun[0:3]
#         for gms in gms_keys:
#             if bks == gms:
#                 new_pbf_data.append(gms_keys[gms])