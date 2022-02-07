import sys
import os
from types import prepare_class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import yaml
from pathlib import Path
from db.db import Database
db = Database()
from config.config import Config


class Profiles:
    def __init__(self, ways_table, filter_ways):

        db = Database()
        self.ways_table = ways_table
        self.filter_ways = filter_ways
        self.batch_size = 200
        self.elevs_interval = 25
        self.var_container = Config('ways').preparation['variable_container']

        conn = db.connect()
        cur = conn.cursor()
        
        cur.execute('''SELECT count(*) FROM {0} {1};'''.format(self.ways_table, self.filter_ways))
        self.total_cnt = cur.fetchall()[0][0]
        
        self.meter_degree = self.var_container['one_meter_degree']

        cur.execute('''SELECT id FROM {0} {1};'''.format(self.ways_table, self.filter_ways))
        ids = cur.fetchall()
        self.ids = [x[0] for x in ids]

        conn.close()
        
        
    def elevation_profile(self): 
        db = Database()
        conn = db.connect() 
        cur = conn.cursor()

        sql_create_table = '''
            DROP TABLE IF EXISTS elevs_{0};
            CREATE TABLE elevs_{0} 
            (
                id bigint,
                elevs float[],
                elevs_interval float,
                length_m float
            );'''.format(self.ways_table)
        cur.execute(sql_create_table)
        conn.commit()
 
        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Slope profile for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()

            sql_elevs = '''
            INSERT INTO elevs_{0}(id, elevs, elevs_interval, length_m)
            WITH way AS 
            (
                SELECT id, geom, length_m
                FROM {0}
                WHERE id = {1}
            )
            SELECT w.id, s.elevs, {2} elevs_interval, w.length_m
            FROM way w, 
            LATERAL (
                SELECT ARRAY_AGG(elev) elevs
                FROM get_elevation_profile_vector(geom, length_m, {3}, {2})
            ) s;'''.format(self.ways_table, i, self.elevs_interval, self.meter_degree)

            cur.execute(sql_elevs)

        conn.commit()

        sql_null_false = '''UPDATE elevs_{0} 
            SET elevs = NULL 
            WHERE ARRAY_LENGTH(elevs,1) = 1
        '''.format(self.ways_table)
        cur.execute(sql_null_false)

        cur.execute('ALTER TABLE elevs_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        conn.commit() 
        conn.close()

    def compute_cycling_impedance(self):
        db = Database()
        conn = db.connect() 
        cur = conn.cursor()
        sql_create_table = '''
            DROP TABLE IF EXISTS impedances_{0};
            CREATE TABLE impedances_{0} 
            (
                id bigint,
                s_imp float,
                rs_imp float
            );'''.format(self.ways_table)
        cur.execute(sql_create_table)
        conn.commit()

        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Compute impedances for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()
            sql_update_impedance = '''
                INSERT INTO impedances_{0}(id, s_imp, rs_imp)
                SELECT x.id, i.imp, i.rs_imp
                FROM (
                    SELECT * 
                    FROM elevs_{0} 
                    WHERE id = {1}
                    AND elevs IS NOT NULL 
                ) x, LATERAL compute_impedances(elevs, length_m, elevs_interval)  i'''.format(self.ways_table, i)
            cur.execute(sql_update_impedance)

        conn.commit()    
        sql_primary_key = 'ALTER TABLE impedances_{0} ADD PRIMARY KEY (id);'.format(self.ways_table)
        cur.execute(sql_primary_key)
        conn.commit()
        conn.close()
    
    def compute_average_slope(self):
        db = Database()
        conn = db.connect() 
        cur = conn.cursor()

        sql_create_table = '''
            DROP TABLE IF EXISTS average_slopes_{0};
            CREATE TABLE average_slopes_{0} 
            (
                id bigint,
                slope float
            );'''.format(self.ways_table)

        cur.execute(sql_create_table)
        conn.commit()
        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Compute slopes for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()

            sql_update_impedance = '''
                INSERT INTO average_slopes_{0}(id, slope)
                SELECT e.id, compute_average_slope(elevs, length_m, elevs_interval) 
                FROM (SELECT * FROM elevs_{0} WHERE id  = {1}) e'''.format(self.ways_table, i)

            cur.execute(sql_update_impedance)

        conn.commit()
        cur.execute('ALTER TABLE average_slopes_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        conn.commit()
        conn.close()

    def create_export_table(self):
        db = Database()
        conn = db.connect() 
        cur = conn.cursor()
        
        sql_merge_tables = '''DROP TABLE IF EXISTS slope_profile_{0};   
        CREATE TABLE slope_profile_{0} AS 
        SELECT e.*, i.s_imp, i.rs_imp, s.slope, w.geom   
        FROM elevs_{0} e
        LEFT JOIN average_slopes_{0} s
        ON e.id = s.id
        LEFT JOIN impedances_{0} i 
        ON e.id = i.id 
        LEFT JOIN {0} w 
        ON e.id = w.id;'''.format(self.ways_table) 

        cur.execute(sql_merge_tables)
        cur.execute('ALTER TABLE slope_profile_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        cur.execute('CREATE INDEX ON slope_profile_{0} USING GIST(geom);'.format(self.ways_table))
        conn.commit()
        conn.close()
    
    def update_line_tables(self):
        db = Database()
        conn = db.connect() 
        cur = conn.cursor()
        if self.ways_table == 'ways':
            sql_update = '''
                UPDATE ways w  
                SET s_imp = s.s_imp, rs_imp = s.rs_imp 
                FROM slope_profile_ways s 
                WHERE ST_EQUALS(w.geom, s.geom) 
            '''
        elif self.ways_table == 'footpaths_visualization': 
            sql_update = '''
                UPDATE footpath_visualization f
                SET incline_percent = slope 
                FROM slope_profile_footpath_visualization s 
                WHERE ST_EQUALS(f.geom, s.geom) 
            '''
        else:
            return {"Error": 'Please specify a valid table!'}
        
        cur.execute(sql_update)
        conn.commit()
        conn.close()

# class PrepareLayers():
#     """Data layers such as population as prepared with this class."""
#     def __init__(self,Database ,is_temp = True):
#         with open(Path(__file__).parent.parent/'config/config.yaml', encoding="utf-8") as stream:
#             config = yaml.safe_load(stream)
#         var = config['Population']
#         self.variable_container = var['variable_container']
#         #self.read_yaml_config = read_yaml_config
#         #self.prepare_db = prepare_db
#         #self.db_conn = db_conn
#         with open(Path(__file__).parent.parent/'config/db.yaml', encoding="utf-8") as stream:
#             db_conf = yaml.safe_load(stream)
#         #self.db_conf = read_yaml_config.return_db_conf()
#         self.db_name = db_conf["DB_NAME"]
#         self.user = db_conf["USER"]
#         self.host = db_conf["HOST"]
#         self.db_suffix = ''
#         if is_temp == True: 
#             self.db_name = self.db_name + 'temp'
#             self.db_suffix = 'temp'
#         self.db = Database()

class PrepareLayers():
    """Data layers such as population as prepared with this class."""
    def __init__(self,layer):
        config = Config(layer)
        var = config.preparation
        self.variable_container = var['variable_container']
        self.db = Database()

    def check_table_exists(self, table_name):
        self.db_conn = self.db.connect()
        return self.db_conn.select('''SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE  table_schema = 'public'
            AND    table_name   = %(table_name)s);''', params={"table_name": table_name})[0][0]


    def ways(self):
        from network_preparation1 import network_preparation1
        self.db.perform(query = network_preparation1)
        from network_islands import network_islands
        self.db.perform(query=network_islands)
        from network_preparation2 import network_preparation2
        self.db.perform(query = network_preparation2)


        # if self.variable_container["compute_slope_impedance"][1:-1] == 'yes':
        #     slope_profiles = Profiles(ways_table='ways', filter_ways=f'''WHERE tag_id::text NOT IN(SELECT UNNEST({self.variable_container['excluded_class_id_cycling']}))''')
        #     if self.check_table_exists('slope_profile_ways') == True: 
        #         slope_profiles.update_line_tables()
        #     else:
        #         print("The table slope_profile_way does not exist")
        #         # import dem

        #         from prepare_dem import prepare_dem 
        #         self.db.perform(query=prepare_dem)
        #         slope_profiles.elevation_profile()
        #         slope_profiles.compute_cycling_impedance()
        #         slope_profiles.compute_average_slope()
        
import time
start_time = time.time()
print("Collection started...")

prep_layers = PrepareLayers('ways')
prep_layers.ways()


print(f"Collection took {time.time() - start_time} seconds ---")