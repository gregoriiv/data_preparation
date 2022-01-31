import sys
import yaml
from pathlib import Path
from config.osm_dict import OSM_tags, OSM_germany

class Config:
    def __init__(self,name):
        with open('src/config/config.yaml', encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
        var = config['VARIABLES_SET']
        self.name = name
        if list(var[name].keys()) == ['collection', 'preparation', 'fusion']:
            self.pbf_data = var['region_pbf']
            self.collection = var[name]['collection']
            self.preparation = var[name]['preparation']
            self.fusion = var[name]['fusion']
        elif list(var[name].keys()) == ['variable_container']:
            self.variable_container = var[name]['variable_container']
        else:
            print("unknown config format")
            sys.exit()

    def pyrosm_filter(self):
        """creates a filter based on user input in the config to filter the OSM import"""
        coll = self.collection

        # check if input osm_tags, osm_features are valid and print non valid ones
        for i in coll["osm_tags"].keys():
            if i not in OSM_tags.keys():
                print(f"{i} is not a valid osm_feature")
        for i in [item for sublist in coll["osm_tags"].values() for item in sublist]:
            if i not in [item for sublist in OSM_tags.values() for item in sublist] + ['all', True]:
                print(f"{i} is not a valid osm_feature")

        # loop collects all tags of a feature from osm_feature_tags_dict.py if "all" in config file
        temp = {}
        for key, values in coll["osm_tags"].items():
            for value in values:
                if value == 'all':
                    temp = temp | {key:OSM_tags[key]}
        
        po_filter = coll["osm_tags"] | temp,None,"keep",list(coll["osm_tags"].keys())+\
                    coll["additional_columns"],coll["points"], coll["lines"],coll["polygons"], None

        return po_filter

    def fusion_key_set(self, typ):
        fus = self.fusion
        try:
            key_set = fus["fusion_data"]['source'][typ].keys()
        except:
            key_set = []
        return key_set

    def fusion_set(self,typ,key):
        fus = self.fusion["fusion_data"]["source"][typ][key]
        fus_set = fus["amenity"],fus["amenity_set"],fus["amenity_operator"],fus["columns2rename"], fus["column_set_value"], fus["columns2fuse"]
        return fus_set
    
    def fusion_type(self, typ, key):
        fus = self.fusion["fusion_data"]["source"][typ][key]
        fus_type = fus["fusion_type"]
        return fus_type

    def network_collection_regions(self):
        regions = self.collection['regions']
        collect = []
        if regions != ['all']:
            for r in regions:
                for key, value in OSM_germany.items():
                    for v in value:
                        if r.lower() in v:
                            if key != "regions":
                                name = key + "/" + v
                                collect.append(f"https://download.geofabrik.de/europe/germany/{name}-latest.osm.pbf")
                            else:
                                collect.append(f"https://download.geofabrik.de/europe/germany/{v}-latest.osm.pbf")
        else:
            for key, value in OSM_germany.items():
                for v in value:
                    if key != "regions": 
                        name = key + "/" + v
                        collect.append(f"https://download.geofabrik.de/europe/germany/{name}-latest.osm.pbf")
                    else:
                        collect.append(f"https://download.geofabrik.de/europe/germany/{v}-latest.osm.pbf")                    
        return collect

def classify_osm_tags(name):
    """helper function to help assign osm tags to their corresponding feature"""
    # import dict from conf_yaml
    with open(Path(__file__).parent/'config/config.yaml', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    var = config['VARIABLES_SET']
    temp = {}
    for key in var[name]['collection']['osm_tags'].keys():
        if key == 'not_sure':
            for i in var[name]['collection']['osm_tags'][key]:
                for keys, values in OSM_tags.items():
                    for value in values:
                        if i == value:
                            if keys in temp.keys():
                                if isinstance(temp[keys], str) is True:
                                    temp[keys] = [temp[keys], i]
                                else:
                                    temp[keys].append(i)
                            else:
                                temp = temp | {keys:i}
                        elif "no_valid_osm_tag" not in temp.keys() and i not in temp.values():
                            temp = temp | {"no_valid_osm_tag":i}
                        elif "no_valid_osm_tag" in temp.keys() and i not in temp["no_valid_osm_tag"]:
                            if isinstance(temp["no_valid_osm_tag"], str) is True:
                                temp["no_valid_osm_tag"] = [temp["no_valid_osm_tag"], i]
                            else:
                                temp["no_valid_osm_tag"].append(i)
            print(temp)
            sys.exit()
