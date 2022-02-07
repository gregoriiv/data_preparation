import subprocess
import os 
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from config.config import Config
from db.config import DATABASE
import pexpect

def password_cmdline(cmd, password):
    child = pexpect.spawn('bash', timeout=20000, ignore_sighup=True)
    child.logfile_read = sys.stdout.buffer
    child.sendline(cmd)
    child.expect('Password:')
    child.sendline(password)
    child.expect('Osm2pgsql took .+ overall')
    child.wait()

def network_collection(conf=None,database=None):
    if not conf:
        conf = Config("ways")
    if not database:
        database = DATABASE

    dbname, host, username, port, password = DATABASE['dbname'], DATABASE['host'], DATABASE['user'], DATABASE['port'], DATABASE['password']
    region_links = conf.collection_regions()
    work_dir = os.getcwd()
    os.chdir('src/data/input') 
    for i, rl in enumerate(region_links):
        subprocess.run(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {rl}', shell=True, check=True)
        subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" --write-xml file="study_area.osm"', shell=True, check=True)
        subprocess.run('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm', shell=True, check=True)
        subprocess.run('rm study_area.osm | mv study_area_reduced.osm study_area.osm', shell=True, check=True)

        os.chdir(work_dir)
        cmd_pgr = f'osm2pgrouting --dbname {dbname} --host {host} --username {username} -p {port} --password {password} --file src/data/input/study_area.osm --conf src/config/mapconfig.xml --chunk 40000'
        if i == 0:
            cmd_pgr = cmd_pgr + ' --clean'
        subprocess.run(cmd_pgr, shell=True, check=True)

        os.chdir('src/data/input')
        if i == 0:
            subprocess.run('cp raw-osm.osm.pbf merged-osm.osm.pbf', shell=True, check=True)
        else:
            subprocess.run('osmosis --read-pbf merged-osm.osm.pbf --read-pbf raw-osm.osm.pbf --merge --write-pbf merged-osm-new.osm.pbf', shell=True, check=True)
            subprocess.run('rm merged-osm.osm.pbf | mv merged-osm-new.osm.pbf merged-osm.osm.pbf', shell=True, check=True)
        
        subprocess.run('rm raw-osm.osm.pbf', shell=True, check=True)
        subprocess.run('rm study_area.osm', shell=True, check=True)

    subprocess.run(f'osmosis --read-pbf file="merged-osm.osm.pbf" --write-xml file="merged_osm.osm"', shell=True, check=True)
    subprocess.run('osmconvert merged_osm.osm --drop-author --drop-version --out-osm -o=merged_osm_reduced.osm', shell=True, check=True)
    subprocess.run('rm merged_osm.osm | mv merged_osm_reduced.osm merged_osm.osm', shell=True, check=True)
    subprocess.run('rm merged-osm.osm.pbf', shell=True, check=True)
    os.chdir(work_dir)
    password_cmdline(f'osm2pgsql -d {dbname} -H {host} -U {username} --port {port} --hstore -E 4326 -W -r .osm -c src/data/input/merged_osm.osm -s --drop -C 24000', password=password)
    os.chdir('src/data/input')
    subprocess.run('rm merged_osm.osm', shell=True, check=True)


# start_time = time.time()
# print("Collection started...")
# network_collection()
# print(f"Collection took {time.time() - start_time} seconds ---")