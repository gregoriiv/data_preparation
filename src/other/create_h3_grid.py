import h3.api.numpy_int as h3
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

class H3Grid:   
    """"This class is used to create a hexgon grid using Uber H3 grid index."""
    def __init__(self):
        self.data_dir = '/app/src/data/output'
    def create_geojson_from_bbox(self, top, left, bottom, right):
        """
        Creates a geojson-like dictionary for H3 from a bounding box
        """
        return {'type': 'Polygon', 'coordinates': [[[bottom, left], [bottom, right], [top, right], [top, left], [bottom, left]]]}

    def create_grid(self, polygon, resolution, layer_name):
        """
        Creates a h3 grid for passed bounding box in SRID 4326
        """
        # Get hexagon ids for selected area and resolution
        hex_ids = h3.polyfill(polygon, resolution, geo_json_conformant=False)

        # Get hexagon geometries and convert to GeoDataFrame
        hex_polygons = lambda hex_id: Polygon(
                                h3.h3_to_geo_boundary(
                                    hex_id, geo_json=True)
                                )           

        hex_polygons = gpd.GeoSeries(list(map(hex_polygons, hex_ids)), 
                                      crs="EPSG:4326" \
                                     )
        hex_ids = pd.Series(hex_ids)
        gdf = gpd.GeoDataFrame(pd.concat([hex_ids,hex_polygons], keys=['id','geometry'], axis=1))
        
        # Save as Geopackage
        gdf.to_file('%s/%s.gpkg' % (self.data_dir,layer_name), driver='GPKG')

# Create grid from bouding box example
#bbox = H3Grid().create_geojson_from_bbox(top=48.352598707539315, left=11.255493164062498, bottom=47.92738566360356, right=11.8927001953125)
#H3Grid().create_grid(polygon=bbox, resolution=9, layer_name='grid_caclulation')
#H3Grid().create_grid(polygon=bbox, resolution=10, layer_name='grid_visualization')