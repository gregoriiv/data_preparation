# import os
# import yaml
from decouple import config

# with open(os.path.dirname(__file__) + "/../config/db.yaml", 'r') as stream:
#     db_conf = yaml.load(stream, Loader=yaml.FullLoader)

DATABASE = {
    'user':     config("POSTGRES_USER"),
    'password': config("POSTGRES_PASSWORD"),
    'host':     config("POSTGRES_HOST"),
    'port':     5432,
    'dbname':   config("POSTGRES_DB")
}

DATABASE_RD = {
    'user':     config("USER_RD"),
    'password': config("PASSWORD_RD"),
    'host':     config("HOST_RD"),
    'port':     config("PORT_RD"),
    'dbname':   config("DB_NAME_RD")
}