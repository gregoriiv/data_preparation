import argparse
from src.export.export_goat import getDataFromSql



ap = argparse.ArgumentParser()

ap.add_argument("-l", "--layers", required=True, help = "Comma separated layer names as the keys from the dictionary or 'all' to be passed e.g study_area,geographical_names,buildings or all")
ap.add_argument("-m", "--municipality", required=True, help = "Comma Separated Codes of the municipality to be passed e.g. 091780124")
ap.add_argument("-t", "--type", help = "Comma Separated Data types. 'sql', 'shp','geojson'. If not passed, default values will be passed.")


args = vars(ap.parse_args())

layers = [layer.strip() for layer in args['layers'].split(',')]
municipalities = [municipality.strip() for municipality in args['municipality'].split(',')]        
if args['type'] is None:
    getDataFromSql(layers, municipalities)
else:    
    types = [type.strip() for type in args['type'].split(',')]
    getDataFromSql(layers, municipalities, export_formats = types)