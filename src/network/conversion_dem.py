import os
import sys
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from db.config import DATABASE
from other.utility_functions import create_pgpass

# Function prepares raster 'tif' file with dem and creates 'dem' table in the local database
# by default filename is 'dtm_germany_20m_v1_sonny'
# !!!CURRENTLY WORKS ONLY LOCALY (THERE IS NO GDAL package pre-installed in docker) 

def conversion_dem(filepath=None):
    if not filepath:
        filepath = 'dtm_germany_20m_v1_sonny'
    
    create_pgpass()
    os.chdir('src/data/dem')
    dbname, host, username, port, password = DATABASE['dbname'], DATABASE['host'], DATABASE['user'], DATABASE['port'], DATABASE['password']
    table_name = 'dem'
    files = [f'{filepath}.sql', f'{filepath}_conv.tif']
    for f in files:
        try:
            os.remove(f)
        except:
            pass

    subprocess.run(f'gdalwarp -t_srs EPSG:4326 -dstnodata -999.0 -r near -ot Float32 -of GTiff {filepath}.tif {filepath}_conv.tif', shell=True, check=True)
    subprocess.run(f'raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 {filepath}_conv.tif public.{table_name} > {filepath}.sql', shell=True, check=True)
    subprocess.run(f'PGPASSFILE=~/.pgpass_{dbname} psql -d %s -U %s -h %s -p %s postgres --command="DROP TABLE IF EXISTS dem" -q' % (dbname,username,host,port), shell=True, check=True)
    subprocess.run(f'PGPASSFILE=~/.pgpass_{dbname} psql -d %s -U %s -h %s -p %s postgres -f %s.sql -q' % (dbname,username,host,port,filepath), shell=True, check=True)

#conversion_dem()