import os
import sys
import time
from pathlib import Path
import geopandas as gp
from decouple import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from db.db import Database

# Function for creation backupfiles
# Convert and save dataframe as GPKG or GeoJSON file formats
# Use it as return result for data preparation functions
def gdf_conversion(gdf, name=None, return_type=None):
    """can convert a GeoGataFrame(gdf) into GeoJSON or GPKG, but always returns the gdf and name"""
    if return_type == "GeoJSON":
        print(f"Writing down the geojson file {name + '.geojson'} ...")
        start_time = time.time()
        gdf.to_file(os.path.join('src', 'data', 'output',  (name +'.geojson')), driver=return_type)
        print(f"Writing file {time.time() - start_time} seconds ---")
        print(f"GeoJSON {name + '.geojson'} was written.")
        return gdf, name
    elif return_type == "GPKG":
        print(f"Writing down the geopackage file {name + '.gpkg'} ...")
        start_time = time.time()
        gdf.to_file(os.path.join('src', 'data', 'output', (name +'.gpkg')), driver=return_type)
        print(f"Writing file {time.time() - start_time} seconds ---")
        print(f"GeoPackage {name + '.gpkg'} was written.")
        return gdf, name
    else:
        return gdf, name

def file2df(filename):
    name, extens = filename.split(".")
    if extens == "geojson":
        file = open(os.path.join('src', 'data', 'input', filename), encoding="utf-8")
        df = gp.read_file(file)
    elif extens == "gpkg":
        file = os.path.join('src', 'data', 'input',filename)
        df = gp.read_file(file)
    else:
        print("Extension of file %s currently doen not support with file2df() function." % filename)
        sys.exit()
    return df     
    
# Create connection to remote database
def rdatabase_connection():
    db = Database()
    con = db.connect_rd()
    return con

# Publish dataframe in REMOTE database  
# df - dataframe, name - table name to store, if_exists="replace" to overwrite datatable
def df2rdatabase(df,name,if_exists='replace'):
    db = Database()
    con = db.connect_rd_sqlalchemy()
    df.to_postgis(con=con, name=name, if_exists=if_exists)


# Returns remote database table as a dataframe 
def database_table2df(con, table_name, geometry_column='geometry'):
    query = "SELECT * FROM %s;" % table_name
    df = gp.read_postgis(con=con,sql=query, geom_col=geometry_column)
    return df

# Create table from dataframe in local database (goat) 
def df2database(df,name,if_exists='replace'):
    db = Database()
    con = db.connect_sqlalchemy()
    df.to_postgis(con=con, name=name, if_exists=if_exists)

def drop_table(table):
    db = Database()
    conn = db.connect() 
    cur = conn.cursor()
    drop_table = '''DROP TABLE IF EXISTS {0};'''.format(table)
    cur.execute(drop_table)
    conn.commit()
    conn.close()

# Create pgpass function
def create_pgpass():
    db_name = config("POSTGRES_DB")    
    try:
        os.system(f'rm ~/.pgpass_{db_name}')
    except:
        pass
    os.system('echo '+':'.join([config("POSTGRES_HOST"),'5432',db_name,config("POSTGRES_USER"),config("POSTGRES_PASSWORD")])+f' > ~/.pgpass_{db_name}')
    os.system(f'chmod 600  ~/.pgpass_{db_name}')

