#%%
"""This module contains all classes and functions for database interactions."""
# Code based on
# https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py
import logging as LOGGER
from multiprocessing import connection
import psycopg2
import sys,os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from db.config import DATABASE
from sqlalchemy import create_engine

#%%
user,password,host,port,dbname = DATABASE.values()

class Database:
    """PostgreSQL Database class."""

    def __init__(self):
        self.conn = None

    def connect_geopandas(self):
        if self.conn is None:
            try:
                # connection object
                self.conn = psycopg2.connect(database = dbname, user = user, password = password,host=host, port=port)
            
            except Exception as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.getLogger().setLevel(LOGGER.INFO)   # To show logging.info in the console
                LOGGER.info('Connection opened successfully.')
        return self.conn

    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                connection_string = " ".join(("{}={}".format(*i) for i in DATABASE.items()))
                # print(connection_string)
                self.conn = psycopg2.connect(connection_string)
            except psycopg2.DatabaseError as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.getLogger().setLevel(LOGGER.INFO)   # To show logging.info in the console
                LOGGER.info('Connection opened successfully.')
        return self.conn

    def connect_sqlalchemy(self):
        print ("Connect to a Postgres database with engine")
        """Connect to a Postgres database with engine"""
        if self.conn is None:
            try:
                self.conn = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
            except Exception as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.info('Connection opened successfully.')
        return self.conn
        
    def select(self, query, params=None):
        """Run a SQL query to select rows from table."""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
            records = cur.fetchall()
        cur.close()
        return records

    def perform(self, query, params=None):
        """Run a SQL query that does not return anything"""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
        self.conn.commit()
        cur.close()

    def mogrify_query(self, query, params=None):
        """This will return the query as string for testing"""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                result = cur.mogrify(query)
            else:
                result = cur.mogrify(query, params)
        cur.close()
        return result

    def fetch_one(self, query, params=None):
        """This will return the next row in the result set"""
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(query)
            if not cur:
                self.send_error(404, f"sql query failed: {(query)}")
                return None
            return cur.fetchone()[0]

    def cursor(self):
        """This will return the query as string for testing"""
        self.connect()
        self.conn.cursor()
        return self.conn.cursor()

#%%
# import geopandas as gpd
# import psycopg2
# from sqlalchemy import create_engine
# from shapely.geometry import Point
# # # test_geo = gpd.read_file('../data/dataframe_all.gpkg')
# # test = test_geo.head()

# # # gdf.to_postgis("my_table", engine)  
# # #%%
# engine_test = psycopg2.connect(database="goat", user="goat", password="postgres",host="localhost", port="55432")
  
# sql_test = "CREATE TABLE geometry_test (name varchar, geom geometry);"
# sql_insert = """INSERT INTO geometries VALUES
#     ('Point', 'POINT(0 0)'),
#     ('Linestring', 'LINESTRING(0 0, 1 1, 2 1, 2 2)'),
#     ('Polygon', 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'),
#     ('PolygonWithHole', 'POLYGON((0 0, 10 0, 10 10, 0 10, 0 0),(1 1, 1 2, 2 2, 2 1, 1 1))'),
#     ('Collection', 'GEOMETRYCOLLECTION(POINT(2 0),POLYGON((0 0, 1 0, 1 1, 0 1, 0 0)))');"""



# engine_test.cursor().execute(sql_test) 
# engine_test.commit()
# gdf_test.to_postgis(gdf_test,engine_test,if_exists='append')
# engine_test.cursor().execute(sql_insert) 
# engine_test.commit()

# conn = psycopg2.connect(database="goat", user="goat", password="postgres",host="localhost", port="55432")

# sql = "CREATE TABLE test3(GID SERIAL PRIMARY KEY, osm_id NUMERIC, building TEXT, amenity TEXT, leisure TEXT, residential_status TEXT, street TEXT, housenumber TEXT, area NUMERIC, building_levels NUMERIC, roof_levels NUMERIC, origin_geometry TEXT, source TEXT, geom GEOMETRY(GEOMETRY, 4326), ags NUMERIC, pred_label NUMERIC, rs TEXT, name TEXT, sum_pop NUMERIC, default_building_levels TEXT, default_roof_levels TEXT, id TEXT, demography TEXT, pop NUMERIC, landuse TEXT, population NUMERIC)"

# df = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='geom' )
# conn.cursor().execute(sql) 
# sql2="select*from landuse"
# df = gpd.GeoDataFrame.from_postgis(sql2, conn, geom_col='geom' )
# test.to_postgis(name='test', con=conn, if_exists='append') 

# conn.commit()
# print('create table')

#%%
# d = {'name': ['name1', 'name2'], 'geometry': [Point(1, 2), Point(2, 1)]}
# gdf_test = gpd.GeoDataFrame(d, crs="EPSG:4326")

# gdf_test
# #%%
# engine_1 = create_engine("postgresql://goat:postgres@localhost:55432/goat")  
# gdf_test.to_postgis("test", engine_1, if_exists='append')  



#%%
# path_file = "E:/Github/data_preparation/src/data/input\landuse_osm2.gpkg"
# import fiona
# layers = fiona.listlayers(path_file)

# for layer in layers:
#     gpd_file =  gpd.read_file(path_file, layer = layer)
#     gpd_file = gpd_file.rename(columns={'geometry': 'geom'}).set_geometry('geom')
#     gpd_file = gpd_file.to_crs("EPSG:" + self.srid)
#     gpd_file.columns = gpd_file.columns.str.replace(r'\W+', '')   
#     gpd_file = gpd_file.loc[gpd_file.is_valid] 

    # files_store.append(self.read_asGPD(file, layer))
# layers = self.select_gpkg_layers(fiona.listlayers(path_file))                                        
# for layer in layers:
#     files_store.append(self.read_asGPD(file, layer)) 
# %%
