import numpy as np
from shapely.geometry import Polygon, LinearRing, mapping
import matplotlib.pyplot as plt
import geopandas as gpd
import os

class CityObject:
    """
        Class to represtent City Objects, and store their geometry in a list which are shapely.polygons
        
    Paramerets:
        gml : gml file
        
        index : index of the object as there are multiple objects in a gml file
    """
    
    def __init__(self, gml, index) -> None:
        self.gml = gml
        self.name = gml["name"][index]
        self.polygons = list()
        for polygon in gml["geometry"][index]:
            ring_array = np.array(mapping(polygon)["coordinates"]).reshape(-1, 3)
            self.polygons.append(Polygon(LinearRing(ring_array)))
        
        
class Road(CityObject):
    """
        Class to represent Roads extended by CityObject
    """
    
    def __init__(self, gml, index) -> None:
        super().__init__(gml, index)
        
    
    
class TrafficSign(CityObject):
    """
        Class to represent Traffic signs extended by CityObject
    """
    
    def __init__(self, gml, index) -> None:
        super().__init__(gml, index)
        
        
        
class Factory:
    """
        Factory to create the demanded objects.
        
        The class creates these Road or TrafficSign objects.
        
    Parameters:
        folder : 'Road' or 'TrafficSign' otherwise raises error
        
        function_id : The ID of the requested object, default value is None as I did not find any information about the functions of the traffic signs
    """
    
    def __init__(self, folder, function_id=None) -> None:
        
        self.folder = folder.lower().strip()
        self.function_id = function_id
        self._road_dir = os.path.join(os.getcwd(), 'Road Kerb')
        self._traffic_sign_dir = os.path.join(os.getcwd(), 'Traffic Sign')
        
        
    def set_road_dir(self, dir) -> None:
        """
        Change the directory of the gml files containing road geometries
        
        Default value is os.path.join(os.getcwd(), 'Road Kerb')
        """
        
        self._road_dir = dir
        
        
    def set_traffic_sign_dir(self, dir) -> None:
        """
        Change the directory of the gml files containing traffic sign geometries
        
        Default value is os.path.join(os.getcwd(), 'Traffic Sign')
        """
        
        self._traffic_sign_dir = dir

        
    def get_road(self, gml, index) -> Road:
        return Road(gml, index)
    
    
    def get_traffic_sign(self, gml, index) -> TrafficSign:
        return TrafficSign(gml, index)
    
    
    def get_folder_info(self) -> tuple:
        return {
            'road' : (self._road_dir, self.get_road),
            'trafficsign' : (self._traffic_sign_dir, self.get_traffic_sign)
                }[self.folder]
        
    
    def get_city_objects(self, bbox = None) -> list:
        """
            Returns a list of the city objects with function_id id if function_id is provided, otherwise returns every object.
        """
        
        directory = self.get_folder_info()[0]
        items = []
        
        for gml_file in os.listdir(directory):
             # Only look for gml files   
            if os.path.splitext(gml_file)[-1] == '.gml':
                # read the file with geopandas
                path = gpd.read_file(os.path.join(directory, gml_file), ignore_fields=('gml_id',
                                                                                       'creationDate',
                                                                                       'class',
                                                                                       'usage',
                                                                                       'usage_',
                                                                                       'relativeToTerrain',
                                                                                       'informationSystem',
                                                                                       'externalReference|externalObject|name',
                                                                                       'surfaceMaterial'), bbox=bbox)
                # list all objects in gml file and append the ones with identical function_id (if function_id is not None) to the items list
                items += [self.get_folder_info()[1](path, index) for index, x in enumerate(path['function']) if self.function_id is None or int(x) == self.function_id]
                
        return items
        
    

class DrivingEnvironment:
    """
        Class to generate Roads and Traffic Signs in an area based on the geojson file
        
    Parameters:
            geojson : path of the geojson file
    """

    def __init__(self, geojson):
        self.geojson_geometry = self.read_geojson(geojson)["geometry"]
        self.road_factory = Factory("Road")
        self.traffic_sign = Factory("TrafficSign")
            
        
    def read_geojson(self, geojson):
        return gpd.read_file(geojson)
    
    
    def generate_roads(self):
        return self.road_factory.get_city_objects(bbox = self.geojson_geometry)
    
    
    def generate_traffic_signs(self):
        return self.traffic_sign.get_city_objects(bbox = self.geojson_geometry)
    
    
    def generate_all(self):
        """
            Generate the Road and Traffic Sign objects.
        """
        
        items = []
        for polygon_list in [x.polygons for x in self.generate_roads()] + [x.polygons for x in self.generate_traffic_signs()]:
            for polygon in polygon_list:
                items.append(polygon)
                
        return items
    
    
    def visualize(self, items=None, **kwargs):
        """
            Visualize the objects
            
        Parameters:
            items : list of geometry, if None, the method will generate the Road and Traffic Sign objects.
            
            **kwargs : kwargs for Geopandas.GeoDataFrame(**kwargs)
        """
        
        if not items:
            items = self.generate_all()
            
        
        gdf = gpd.GeoDataFrame(
            {
                'geometry' :  items
            })
        
        gdf.plot(**kwargs)
        plt.show()
        
        
        

if __name__ == '__main__':
    env = DrivingEnvironment(os.getcwd(), "arae.geojson")
    items = env.generate_all()
    env.visualize(items, figsize=(6, 6))
    
    
    
    
   
    
    
        
       