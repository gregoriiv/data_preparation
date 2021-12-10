#%%
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from pathlib import Path
from db.db import Database
db = Database()


# 1. access database
# 2. access data -> change paths
# 3. write script to execute sql scripts as strings
# 4. how to deal with the container -> move to Config YAML -> sql scripts as fstrings -> input information from Config

# preparation: add helper functions, so they can be performed later on
# db.perform...

# data_fusion_buildings + helper function get_id_for_max_val
from get_id_for_max_val import get_id_for_max_val
db.perform(query = get_id_for_max_val)
from data_fusion_buildings import data_fusion_buildings
db.perform(query = data_fusion_buildings)

# classify_buildings + helper functions jsonb_array_int_array, derive_dominant_class, classify_building
from jsonb_array_int_array import jsonb_array_int_array
db.perform(query = jsonb_array_int_array)
from derive_dominant_class import derive_dominant_class
db.perform(query = derive_dominant_class)
from classify_building import classify_building
db.perform(query = classify_building)
#Create db extensions (should be added when creating the database?)
db.perform(query = "CREATE EXTENSION IF NOT EXISTS intarray;")
# landuse additional currently commented out as the data is missing for Nuernberg
from classify_buildings import classify_buildings
db.perform(query = classify_buildings)

# create_residential_addresses + helper function meter_degree
from meter_degree import meter_degree
db.perform(query = meter_degree)
# create_residential_addresses
from create_residential_addresses import create_residential_addresses
db.perform(query = create_residential_addresses)

# Census
# prepare_census

# census_standard: population_census
# census_extrapolation: population_extrapolated_census
# census_disaggregation: population_disaggregation
# custom_population: print(“Custom population will be used”)
# print('No valid population mode was provided. Therefore the population scripts cannot be execute