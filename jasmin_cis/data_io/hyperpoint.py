from collections import namedtuple
# Radius of the earth in Km
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
        if val is None or val == []:
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
            
    def get_coord_tuple(self):
        return [ (x, y) for x, y in self._asdict().items() if y is not None and x != 'val' ]

    def compdist(self,p1,p2):
        '''
            Compares the distance from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.haversine(p1.latitude,p1.longitude) > self.haversine(p2.latitude,p2.longitude))
    
    def haversine(self,lat2,lon2):
        '''
            Computes the Haversine distance between two points
        '''
        import math
        lat1 = self.latitude * math.pi / 180
        lat2 = lat2 * math.pi / 180
        lon1 = self.longitude * math.pi / 180
        lon2 = lon2 * math.pi / 180
        arclen = 2*math.asin(math.sqrt((math.sin((lat2-lat1)/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2-lon1)/2))**2))
        return arclen*R_E
    
    def furthest_point_from(self):
        '''
            Return a point on the opposite side of the globe from this point
        '''
        furthest_lat = -self.latitude
        if self.longitude > 180:
            furthest_lon = self.longitude - 180.0
        else:
            furthest_lon = self.longitude + 180.0
        return HyperPoint(furthest_lat, furthest_lon, self.altitude, self.time, self.val)


def get_coordinates_points(coords):
    # Pack the data into a list of x,y, val points to be passed to col
    points = []

    for lat_p in dims.lat[:]:
        for lon_p in dims.lon[:]:
            for alt_p in dims.alt[:]:
                for time_p in dims.time[:]:
                    points.append(HyperPoint(lat_p,lon_p,alt_p,time_p))

    return points
