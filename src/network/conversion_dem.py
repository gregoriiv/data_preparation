import os
import sys
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from db.config import DATABASE
from db.db import Database
from decouple import config


print(config('TEST'))

#work_dir = os.getcwd()
os.chdir('src/data/dem')

dbname, host, username, port, password = DATABASE['dbname'], DATABASE['host'], DATABASE['user'], DATABASE['port'], DATABASE['password']
db = Database()

filepath = 'dtm_germany_20m_v1_sonny'
table_name = 'dem'

subprocess.run(f'gdalwarp -t_srs EPSG:4326 -dstnodata -999.0 -r near -ot Float32 -of GTiff {filepath}.tif {filepath}_conv.tif', shell=True, check=True)
# # #  -s_srs EPSG:4258
subprocess.run(f'raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 {filepath}_conv.tif public.{table_name} > {filepath}.sql', shell=True, check=True)
subprocess.run(f'psql -d %s -U %s -h %s -p %s postgres -f %s.sql -q' % (dbname,username,host,port,filepath), shell=True, check=True)
