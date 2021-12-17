from geopy import geocoders
from geopy import Nominatim
from geojson import Point
import json


class GeoAddress:
  def __init__(self, street=None, houseno=None, city=None, country=None, postcode=None):
    self.street = street if street is not None else 'addr:street'
    self.houseno = houseno if houseno is not None else ''
    self.city = city if city is not None else 'addr:city'
    self.country = country if country is not None else 'addr:country'
    self.postcode = postcode if postcode is not None else 'addr:postcode'

def getValue(d, attr):
    if attr != "":
        for k, v in d.items():
            if isinstance(v, dict):
                return getValue(v, attr)
            elif ("{}".format(k)) == attr:
                try:
                    return "{}".format(v)
                except:
                    return ""
    else:
        return ""

def addLocationOfAdressToJson(input_fpath,output_fpath,g_api_key,addr_class):
    g = geocoders.GoogleV3(api_key=g_api_key)
    osm = Nominatim(user_agent = "goat_community")

    j_file = open(input_fpath,"r+",encoding="utf-8")
    data = json.load(j_file)

    for i in data['features']:
        address = getValue(i,addr_class.street)+ ' ' + getValue(i, addr_class.houseno)+ ' ' + getValue(i, addr_class.city)+ ' ' + getValue(i, addr_class.country)+ ' '+ getValue(i, addr_class.postcode)
        try:
            location = g.geocode(address)
            g_point = Point((location.longitude, location.latitude))
            i.pop('geometry')
            i['geometry'] = g_point
        except:
            try:
                location = osm.geocode(address)
                osm_point = Point((location.longitude, location.latitude))
                i['geometry'] = osm_point
            except:
                pass

    with open(output_fpath, 'w') as j_file:
        json.dump(data, j_file)



# path = "data\input\denns_de_upd.geojson"
# path2store = "data\output\denns_de_upd.geojson"

# addr = GeoAddress(street="addr:street", city="addr:city", country="addr:country", postcode="addr:postcode")
# addLocationOfAdressToJson(path,path2store,google_api_key,addr)