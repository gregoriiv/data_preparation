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

# restore all sql dumbs within container + import landuse_osm.gpkg and buildings_osm.gpkg via GQIS
#######

# # data_fusion_buildings + helper function get_id_for_max_val
# from get_id_for_max_val import get_id_for_max_val
# db.perform(query = get_id_for_max_val)
# from data_fusion_buildings import data_fusion_buildings
# db.perform(query = data_fusion_buildings)

# # classify_buildings + helper functions jsonb_array_int_array, derive_dominant_class, classify_building
# from jsonb_array_int_array import jsonb_array_int_array
# db.perform(query = jsonb_array_int_array)
# from derive_dominant_class import derive_dominant_class
# db.perform(query = derive_dominant_class)
# from classify_building import classify_building
# db.perform(query = classify_building)
# #Create db extensions (should be added when creating the database?)
# db.perform(query = "CREATE EXTENSION IF NOT EXISTS intarray;")
# from classify_buildings import classify_buildings
# db.perform(query = classify_buildings)

####
# create planet_osm_points

# from pyrosm import get_data, OSM
# downloading lastest .osm.pbf from Geofabrik or BBBike
# fp = get_data("Mittelfranken", directory = Path.cwd()/'data', update = True)
# print("Data was downloaded to:", fp)

# for Nürnberg run in container (before start container using command line: docker-compose up -d and ssh into container: docker exec -it db_data_preparation /bin/bash)
# https://www.openstreetmap.org/export#map=11/49.4471/11.1525 for the bounding box
# osmosis --read-pbf file="src/data/mittelfranken-latest.osm.pbf" --bounding-box top=49.5742 left=10.8861 bottom=49.3009 right=11.3331 --write-xml file="src/data/study_area.osm"

#Create db extensions (should be added when creating the database?)
#db.perform(query = "CREATE EXTENSION IF NOT EXISTS hstore;")
# run in container (before start container using command line: docker-compose up -d and ssh into container: docker exec -it db_data_preparation /bin/bash)
# osm2pgsql -d goat -H localhost -U goat --password --hstore -E 4326 -c src/data/study_area.osm

####

# # create_residential_addresses + helper function meter_degree
# db.perform(query = meter_degree)
# from create_residential_addresses import create_residential_addresses
# db.perform(query = create_residential_addresses)

# # Census -> prepare census + extrapolation, disaggregation, custom population
# from prepare_census import prepare_census
# db.perform(query = prepare_census)

# census_standard: population_census
# from population_census import population_census
# db.perform(query = population_census)

# census_extrapolation: population_extrapolated_census
# from population_extrapolated_census import population_extrapolated_census
# db.perform(query = population_extrapolated_census)

# census_disaggregation: population_disaggregation
from population_disaggregation import population_disaggregation
db.perform(query = population_disaggregation)

# custom_population: print(“Custom population will be used”)
# print('No valid population mode was provided. Therefore the population scripts cannot be execute


#### TO-DO:
# Schleife/ Klasse drumrumbauen mit Userinput bzgl. census_extrapolation, census_disaggregation, custom_population or Print('no valid...')