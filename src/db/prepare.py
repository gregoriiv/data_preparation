import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
# print(sys.path[0])
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from db.db import Database


class PrepareDB:
    def __init__(self, Database):
        self.db = Database()

    def read_as_str(self, path, file_name): # read sql file as text input
        sqltxt = open(path + file_name, 'r', encoding = 'utf8').read()

        return sqltxt

    def create_db_functions(self):
        """This function prepares the database to run the function produce_population_points()."""
        path = "src/db/functions/"

        self.db.perform(query = self.read_as_str(path, 'get_id_for_max_val.sql'))
        self.db.perform(query = self.read_as_str(path,'classify_building.sql'))
        self.db.perform(query = self.read_as_str(path, 'jsonb_array_int_array.sql'))
        self.db.perform(query = self.read_as_str(path,'derive_dominant_class.sql'))
        print("==== preparation function finished ====")
        
    def create_db_extensions(self):
        # Create db extensions (should be added when creating the database?)
        self.db.perform(query = "CREATE EXTENSION IF NOT EXISTS intarray;")

preparation = PrepareDB(Database)
preparation.create_db_functions()
preparation.create_db_extensions()