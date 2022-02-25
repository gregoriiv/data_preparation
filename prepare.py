import argparse, sys, os
from argparse import RawTextHelpFormatter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from src.other.utility_functions import database_table2df, df2database, drop_table
from src.collection import osm_collection
from src.preparation import pois_preparation
from src.fusion import pois_fusion
from src.network.network_collection import network_collection
from src.network.ways import PrepareLayers, Profiles

from src.db.db import Database
from src.db.prepare import PrepareDB


#Define command line options

layers_prepare = ['network', 'pois']
layers_fuse = ['pois']

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-db',help='Create neccesary extensions and functions for fresh database', action='store_true')
parser.add_argument('-prepare',help='Please specify layer name for data collection and preparation from osm (e.g. pois, network)')
parser.add_argument('-fuse',help='Please specify layer name for data fusion from osm (e.g. pois, network)')
args = parser.parse_args()
prepare = args.prepare
fuse = args.fuse


if args.db == True:
    prepare_db = PrepareDB(Database)
    prepare_db.create_db_functions()
    prepare_db.create_db_extensions()

if prepare or prepare in(layers_prepare):
    if prepare == 'network':
        network_collection()
        prep_layers = PrepareLayers('ways')
        prep_layers.ways()
    elif prepare == 'pois':
        pois = osm_collection('pois')[0]
        pois = pois_preparation(pois)[0]
        drop_table('pois')
        df2database(pois, 'pois')
    else:
        print('Please specify a valid preparation type.')

if fuse or fuse in(layers_fuse):
    if fuse == 'pois':
        db = Database()
        con = db.connect()
        pois = database_table2df(con, 'pois', geometry_column='geom')
        pois = pois_fusion(pois)[0]
        drop_table('pois_fused')
        df2database(pois, 'pois_fused')
        