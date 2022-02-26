# Data preparation
This is a repository containing the data preparation steps for GOAT. 


# Start Database Docker Container and Connect

1. Rename .env_template file to .env
2. Run `docker-compose up -d`
3. Connect using the credentials defined in .env
4. Use command line to prepare database `python prepare.py -db`.

#  Prepare Layers and Store it in Local Database

5. Configure preparation settings in `src/config/config.yaml` *See documentation 
6. Use command line to prepare layers in database tables `python prepare.py -prepare LAYERNAME` (pois, network, landuse, buildings)

# (Optional) Fuse Custom Data with Stored One

7. Configure fusion settings in `src/config/config.yaml` *See documentation
8. In case of use of data from geonode, specify credidentials defined in .env for remote database
9. Use command line to fuse data and store in layers in database tables `python prepare.py -fuse LAYERNAME` (pois)


