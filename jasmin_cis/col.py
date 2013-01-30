'''
    Colocation routines - to be implemented
'''
from collections import namedtuple
R_E = 6378

# Data type representing a point in space and time. It can contain multiple values which are stored in a list
#HyperPointT = namedtuple('HyperPoint',['latitude','longitude','altitude','time','val'])

class HyperPoint(namedtuple('HyperPoint',['latitude','longitude','altitude','time','val'])):
    
    def __new__(cls, lat=None, lon=None, alt=None, t=None, val=None):
        '''
            Small constructor for the HyperPoint named tuple to allow optional arguments
             and set-up value list.
        '''
        # If no value was specified create an empty list, otherwise create a list with one entry   
        if val is None:
            val = []
        else:
            val = [ val ]
        return super(HyperPoint,cls).__new__(cls,lat,lon,alt,t,val)

    def same_point_in_time(self, other):
        return self.time == other.time
        
    def same_point_in_space(self, other):
        return ( self.latitude == other.latitude and self.longitude == other.longitude and
                 self.altitude == other.altitude )
    
    def same_point_in_space_and_time(self, other):
        return ( self.same_point_in_space(other) and self.same_point_in_time(other) )
            
            
def get_coord_tuple(point):
    return [ (x, y) for x, y in point._asdict().items() if y is not None and x != 'val' ]

def compdist(ref_p,p1,p2):
    '''Compares the distance from reference point ref_p to p1 and p2. Returns True if p2 is closer to ref_p than p1'''
    #print (haversine(latp,lonp,lat1,lon1), haversine(latp,lonp,lat2,lon2))
    #if not np.isfinite(haversine(latp,lonp,lat1,lon1)):
    #    return True
    return (haversine(ref_p.lat,ref_p.lon,p1.lat,p1.lon) > haversine(ref_p.lat,ref_p.lon,p2.lat,p2.lon))

def haversine(lat1,lon1,lat2,lon2):
    import math
    '''Computes the Haversine distance between two points'''
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    arclen = 2*math.asin(math.sqrt((math.sin((lat2-lat1)/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2-lon1)/2))**2))
    return arclen*R_E

def furthest_point_from(lat,lon):
    '''
        Return the furthest point along the surface of the globe from a given latitude and longitude
    '''
    if lat > 0:
        furthest_lat = lat - 90.0
    else:
        furthest_lat = lat + 90.0
    if lon > 180:
        furthest_lon = lon - 180.0
    else:
        furthest_lon = lon + 180.0
    return HyperPoint(furthest_lat, furthest_lon)

class Colocator(object):

    def __init__(self, points, data, col_method='nn', constraints=None):
        from jasmin_cis.exceptions import InvalidColocationMethodError
        from iris import cube
        
        self.points = points
        self.data = data
        self.constraints = constraints        
        
        if isinstance(data, cube.Cube):  
            methods = Colocator.gridded_colocation_methods._asdict()
        else:
            methods = Colocator.ungridded_colocation_methods._asdict()
            
        self.method = methods[col_method]
               
        if self.method is None:
            raise InvalidColocationMethodError('This co-location method is invalid for this data type')
                
    def colocate(self):
        for point in self.points:
            point.val.append(self.method(self, point))
        
    def find_nn_value(self, point):
        '''
            Colocation using nearest neighbours without any constraints where both points and 
              data are a list of HyperPoints
        '''
        nearest_point = furthest_point_from(point)
        for data_point in self.data:
            if compdist(data_point,nearest_point,point): nearest_point = data_point
        return nearest_point.val
    
    def find_nn_value_ungridded(self, point, constraint_fn=None):
        '''
            Co-location routine using nearest neighbour algorithm optimized for ungridded data
        '''
        import numpy as np
        nearest_point = furthest_point_from(point)
        for (x,y), value in np.ndenumerate(self.data.vals):
            ug_point = HyperPoint(self.data.lat[x,y],self.data.lon[x,y],val=value)
            if compdist(ug_point,nearest_point,point): nearest_point = ug_point
            
        if constraint_fn is not None:
            return constraint_fn(point, nearest_point)
        else:
            return nearest_point.val
    
    def find_nn_value_gridded(self, point):
        '''
            Co-location routine using nearest neighbour algorithm optimized for gridded data.
             This calls out to iris to do the work.
        '''
        from iris.analysis.interpolate import nearest_neighbour_data_value
        return nearest_neighbour_data_value(self.data, get_coord_tuple(point))
    
    def find_value_by_li(self, point):
        pass
    
    ColocationTechniques = namedtuple('Techniques',['nn', 'li'])
    gridded_colocation_methods = ColocationTechniques(find_nn_value_gridded, find_value_by_li)
    ungridded_colocation_methods = ColocationTechniques(find_nn_value_ungridded, None)

