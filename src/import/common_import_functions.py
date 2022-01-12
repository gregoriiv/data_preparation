import glob
import pandas as pd
import geopandas as gpd
from db.db import Database
import fiona
import logging as LOGGER
import re

#Create Postgresql Engine
db = Database()
engine = db.connect_engine()


def initialize_import(args):
    """
        Import bulk shape, geojson and gpkg files to PostGIS
    """ 
    if args['dir'].endswith('/'):
        args['dir'] = args['dir'][:-1]
    if args['table_name'] is None:
        args['table_name'] = args['dir'].split('/')[-1]
    bulk_import = BulkImport(args)
    bulk_import.create_files_path(args['type'])
    bulk_import.bulk_import_files()

class BulkImport:

    def __init__(self, args):
        self.dir = args['dir']
        self.srid = args['srid']
        self.discard_files = args['discard_files']
        self.prefix = args['prefix']
        self.middle = args['middle']
        self.sufix = args['sufix']
        self.table_name = args['table_name']
        self.insert_type = args['insert_type']        


    def read_asGPD(self, file, layer = None):
        """
            Read file as geo pandas frame
        """
        gpd_file = None
        
        if type(file) is dict:
            #Read validated geojson object
            gpd_file = gpd.GeoDataFrame.from_features(file)
            gpd_file.set_crs(epsg=4326, inplace=True)
        elif layer is None:
            #Read shapefile
            gpd_file =  gpd.read_file(file)
        else:
            #Read layer from geopackage
            gpd_file =  gpd.read_file(file, layer = layer)

        gpd_file = gpd_file.rename(columns={'geometry': 'geom'}).set_geometry('geom')
        gpd_file = gpd_file.to_crs("EPSG:" + self.srid)
        gpd_file.columns = gpd_file.columns.str.replace(r'\W+', '')   
        gpd_file = gpd_file.loc[gpd_file.is_valid]    
        return gpd_file


    def validateGeoJson(self, file):
        """
            Validate GeoJson file
        """    
        json_file = pd.read_json(file)
        geojson = {"type":"FeatureCollection","features":[]}
        for i in range(len(json_file)):
            row = json_file['features'][i]
            for key, value in row['properties'].items():            
                if type(value) is list:
                    row['properties'][key] = ",".join(value)
            if 'geometry' in row:
                geojson['features'].append(row)

        return geojson


    def select_gpkg_layers(self, layers):
        """
            select gpkg layers based on filters(prefix, middle and sufix)
        """
        selected_layers = []

        if self.prefix is not None:
            selected_layers.extend(list(filter(lambda layer: layer.startswith(self.prefix), layers)))

        if self.middle is not None:
            selected_layers.extend(list(filter(lambda layer: layer[1:-1].find(self.middle) == 1, layers)))        

        if self.sufix is not None:
            selected_layers.extend(list(filter(lambda layer: layer.endswith(self.sufix), layers)))    

        if len(selected_layers) == 0:
            return layers
        else:   
            print('Geopackages layers filtered based on prefix, middle or sufix passed by user') 
            print(f'''Selecting layers {selected_layers}''')    
            return list(set(selected_layers))        


    def read_files(self):
        """
            Read files from path and return them as a list of geopandas frame
            Parameter files is a list of files path
        """
        files_store = []   
        print('Processing and validating files before importing') 
        for file in self.files:
            try:            
                if file.endswith('.gpkg'):
                    #Select gpkg layers based on filters(prefix, middle and sufix) and read them
                    layers = self.select_gpkg_layers(fiona.listlayers(file))                                        
                    for layer in layers:
                        files_store.append(self.read_asGPD(file, layer))   
                elif  file.endswith('.geojson'):
                    #Validate and read geojson  file
                    files_store.append(self.read_asGPD(self.validateGeoJson(file)))
                else:       
                    #Read shapefile
                    files_store.append(self.read_asGPD(file))
                print(f'''{file} processed''')
            except Exception as e:                
                print(f'''{file} file is discarded because file is either empty or invalid.''')
                print(e)

        return files_store


    def creaeTableQueryFromGPD(self, gdf):
        """
            Create a table query for geopandas file based on the columns list
        """
        create_table_query = 'GID SERIAL PRIMARY KEY'
        #create table query for common columns
        for column in gdf.columns:
            column_type = str(gdf.dtypes[column])
            if column == "geom":
                create_table_query += ', geom GEOMETRY(GEOMETRY, 4326)'
            elif column_type.find('int') != -1:
                create_table_query += ', ' + column + ' INTEGER'
            elif column_type.find('float') != -1:
                create_table_query += ', ' + column + ' NUMERIC'
            else:
                create_table_query += ', ' + column + ' TEXT'

        return  'CREATE TABLE ' + self.table_name + '(' + create_table_query + ')'


    def insert_gdf_to_postgis(self, gdf):
        """
            insert geodataframe created into postgres table
        """
        try:
            gdf.to_postgis(self.table_name, con=engine, if_exists='append') 
        except Exception as e :
            raise e
        finally:
            print('Data inserted successfully.')


    def create_files_path(self, ext):
        """
            Get list of files from the path recursively
        """
        self.files = glob.glob(self.dir + '/**/*.' + ext, recursive=True)


    def discardfiles(self):
        """
            Discard files
        """
        if self.discard_files is not None:
            d_files = self.discard_files.split(',')
            for d_file in d_files:
                for i in range(len(self.files)):
                    if self.files[i].split('/')[-1].split('.')[0] == d_file.strip():
                        print(f'''{self.files[i]} discarded as per user's request''')
                        self.files.pop(i)
                        break


    def bulk_import_files(self):
        """
            Import bulk files to PostGIS
        """         

        #Discarding given files
        self.discardfiles()

        #Read files using geopadas and return them as list
        files_store = self.read_files()      
        for i in files_store:
            print(i.dtypes)    

        if len(files_store) == 0:
            print("No files selected to import because selected directory is either empty or contain invalid files.")
            raise "No files selected to import because selected directory is either empty or contain invalid files."          

        #Concatenate all gpd frames into one
        gdf = gpd.GeoDataFrame(pd.concat([i for i in files_store], ignore_index=True))
        gdf = gdf.set_geometry('geom')
        print(gdf.dtypes)

        print('All valid files processed successfully')        
        
        #Create table query
        if self.insert_type == 'create':
            create_table_query = self.creaeTableQueryFromGPD(gdf)                      
            engine.execute(create_table_query)    
            print("{} table created successfully".format(self.table_name))

        print("Importing files...")
        #Inserting record to table            
        
        #Import geopandas file to PostGIS
        gdf.columns = gdf.columns.str.lower()          
        self.insert_gdf_to_postgis(gdf)                          
        print('All valid files imported successfully')

        #Create spatial index      
        if self.insert_type == 'create':  
            create_spatial_index = 'CREATE INDEX ON ' + self.table_name + ' USING GIST(geom)'
            engine.execute(create_spatial_index)            
            print(f'''Spatial Index created for {self.table_name} table''')