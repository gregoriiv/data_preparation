import argparse, sys, os
from argparse import RawTextHelpFormatter
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from src.other.utility_functions import database_table2df, df2database, drop_table, migrate_table2localdb2
from src.collection.collection import osm_collection
from src.collection.preparation import pois_preparation, landuse_preparation, buildings_preparation
from src.collection.fusion import pois_fusion
from src.network.network_collection import network_collection
from src.network.ways import PrepareLayers, Profiles
from src.network.conversion_dem import conversion_dem
from src.population.population_data_preparation import population_data_preparation
from src.population.produce_population_points import Population
from src.export.export_goat import getDataFromSql
from src.export.export_tables2basic import sql_queries_goat
from src.network.network_islands_municip import calculate_network_islands_mun

from src.db.db import Database
from src.db.prepare import PrepareDB


#Define command line options

layers_prepare = ['aoi', 'dem', 'building', 'network', 'study_area', 'population', 'grid_visualization', 'grid_calculation', 'poi']

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-p','--prepare', required=True, help='Please specify layer name for data preparation for goat (e.g. pois, network, population, buildings, etc)')
parser.add_argument("-m", "--municipality", required=True, help = "Comma Separated Codes of the municipality to be passed e.g. 091780124")

args = vars(parser.parse_args())
prepare = args['prepare']

municipalities = [municipality.strip() for municipality in args['municipality'].split(',')]   

if prepare or prepare in(layers_prepare):
    if prepare == 'population':
        population_data_preparation(municipalities)
        population = Population(Database=Database)
        population.produce_population_points(source_population = 'census_extrapolation')
    elif prepare == 'network':
        getDataFromSql('ways', municipalities)
        migrate_table2localdb2('study_area')
        migrate_table2localdb2('ways')
        migrate_table2localdb2('ways_vertices_pgr')
        for m in municipalities:
            calculate_network_islands_mun(m)
        db = Database()
        conn = db.connect()
        cur = conn.cursor()
        rename_tables = '''
            DROP TABLE IF EXISTS temporal.edge;
            DROP TABLE IF EXISTS temporal.node;
            CREATE TABLE temporal.edge AS TABLE temporal.ways;
            CREATE TABLE temporal.node AS TABLE temporal.ways_vertices_pgr;'''
        cur.execute(rename_tables)
        conn.commit()
        db.perform(sql_queries_goat['nodes_edges'])
        conn.close()
