import subprocess
import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from config.config import Config
from db.config import DATABASE

def network_collection(conf=None,database=None):
    if not conf:
        conf = Config("ways")
    if not database:
        database = DATABASE

    dbname, host, username, port, password = DATABASE['dbname'], DATABASE['host'], DATABASE['user'], DATABASE['port'], DATABASE['password']
    flag = True
    region_links = conf.network_collection_regions()
    work_dir = os.getcwd()
    os.chdir('src/data/input') 
    for rl in region_links:
        subprocess.run(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {rl}', shell=True, check=True)
        subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" --write-xml file="study_area.osm"', shell=True, check=True)
        subprocess.run('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm', shell=True, check=True)
        subprocess.run('rm study_area.osm | mv study_area_reduced.osm study_area.osm', shell=True, check=True)
        subprocess.run('rm raw-osm.osm.pbf', shell=True, check=True)

        os.chdir(work_dir)
        if flag:
            subprocess.run(f'osm2pgrouting --dbname {dbname} --host {host} --username {username} -p {port} --password {password} --file src/data/input/study_area.osm --conf src/config/mapconfig.xml --clean --chunk 40000', shell=True, check=True)
            flag = False
        else:
            subprocess.run(f'osm2pgrouting --dbname {dbname} --host {host} --username {username} -p {port} --password {password} --file src/data/input/study_area.osm --conf src/config/mapconfig.xml --chunk 40000', shell=True, check=True)
        
        os.chdir('src/data/input') 
        subprocess.run('rm study_area.osm', shell=True, check=True)


network_collection()