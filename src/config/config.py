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
        if list(var[name].keys()) == ['region_pbf','collection', 'preparation', 'fusion']:
            self.pbf_data = var[name]['region_pbf']
            self.collection = var[name]['collection']
            self.preparation = var[name]['preparation']
            self.fusion = var[name]['fusion']
        else:
            print("unknown config format")
            sys.exit()

    def osm_object_filter(self):
        osm_tags = self.collection["osm_tags"]
        osm_nodes = self.collection["points"]
        osm_poly = self.collection["polygons"]
        osm_lines = self.collection["lines"]
        object_filter = ''
        for i in osm_tags:
            string = i
            for j in osm_tags[i]:
                if j == True:
                    all_tags = OSM_tags[i]
                    string = i
                    for t in all_tags:
                        string += ('=' + t)
                        string += (' ') 
                else:
                    string += ('=' + j)
                    string += (' ')
            object_filter += string
        object_filter = '"' + object_filter + '" '

        if not osm_nodes:
            object_filter += '--drop-nodes '
        if not osm_poly:
            object_filter += '--drop-relations '
        if not osm_lines:
            object_filter += '--drop-ways '

        request = f'osmfilter raw-merged-osm.osm --keep={object_filter} -o=osm-filtered.osm'

        return request

    def osm2pgsql_create_style(self):
        add_columns = self.collection['additional_columns']
        osm_tags = self.collection["osm_tags"]
        pol_columns = ['amenity', 'leisure', 'tourism', 'shop', 'sport', 'public_transport']

        f = open("src/config/style_p4b.style", "r")
        sep = '#######################CUSTOM###########################'
        text = f.read()
        text = text.split(sep,1)[0]

        f1 = open(f"src/config/{self.name}_p4b.style", "w")
        f1.write(text)
        f1.write(sep)
        f1.write('\n')

        print(f"Creating osm2pgsql style file({self.name}_p4b.style)...")
        for column in add_columns:
            if column in pol_columns:
                style_line = f'node,way  {column}  text  polygon'
                f1.write(style_line)
                f1.write('\n')                 
            else:
                style_line = f'node,way  {column}  text  linear'
                f1.write(style_line)
                f1.write('\n')  
        
        for tag in osm_tags:
            if tag in ['railway', 'highway']:
                style_line = f'node,way  {tag}  text  linear'
                f1.write(style_line)
                f1.write('\n')  
            else:
                style_line = f'node,way  {tag}  text  polygon'
                f1.write(style_line)
                f1.write('\n')                  

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

    def collection_regions(self):
        regions = self.pbf_data
        collect = []
        if regions == ['all']:
            for key, value in OSM_germany.items():
                for v in value:
                    if key != "regions": 
                        name = key + "/" + v
                        collect.append(f"https://download.geofabrik.de/europe/germany/{name}-latest.osm.pbf")
                    else:
                        collect.append(f"https://download.geofabrik.de/europe/germany/{v}-latest.osm.pbf")   

        elif regions == ['Germany']:
            collect.append("https://download.geofabrik.de/europe/germany-latest.osm.pbf")
        elif regions == ['Bayern']:
            collect.append("https://download.geofabrik.de/europe/germany/bayern-latest.osm.pbf")
        else:
            for r in regions:
                for key, value in OSM_germany.items():
                    for v in value:
                        if r.lower() in v:
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

    # # OUTDATED
    # def pyrosm_filter(self):
    #     """creates a filter based on user input in the config to filter the OSM import"""
    #     coll = self.collection

    #     # check if input osm_tags, osm_features are valid and print non valid ones
    #     for i in coll["osm_tags"].keys():
    #         if i not in OSM_tags.keys():
    #             print(f"{i} is not a valid osm_feature")
    #     for i in [item for sublist in coll["osm_tags"].values() for item in sublist]:
    #         if i not in [item for sublist in OSM_tags.values() for item in sublist] + ['all', True]:
    #             print(f"{i} is not a valid osm_feature")

    #     # loop collects all tags of a feature from osm_feature_tags_dict.py if "all" in config file
    #     temp = {}
    #     for key, values in coll["osm_tags"].items():
    #         for value in values:
    #             if value == 'all':
    #                 temp = temp | {key:OSM_tags[key]}
        
    #     po_filter = coll["osm_tags"] | temp,None,"keep",list(coll["osm_tags"].keys())+\
    #                 coll["additional_columns"],coll["points"], coll["lines"],coll["polygons"], None

    #     return po_filter