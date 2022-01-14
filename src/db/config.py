from ast import Or
import os
import yaml


with open(os.path.dirname(__file__) + "/../config/db.yaml", 'r') as stream:
        db_conf = yaml.load(stream, Loader=yaml.FullLoader)

DATABASE = {
    'user':     os.environ['USER'] or db_conf['USER'],
    'password': db_conf["PASSWORD"],
    'host':     db_conf["HOST"],
    'port':     db_conf["PORT"],
    'dbname': db_conf["DB_NAME"]
}

DATABASE_RD = {
    'user':     db_conf["USER_RD"],
    'password': db_conf["PASSWORD_RD"],
    'host':     db_conf["HOST_RD"],
    'port':     db_conf["PORT_RD"],
    'dbname': db_conf["DB_NAME_RD"]
}