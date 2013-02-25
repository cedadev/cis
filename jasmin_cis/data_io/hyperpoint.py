from collections import namedtuple

class HyperPoint(namedtuple('HyperPoint',['latitude','longitude','altitude','time','val'])):
    '''
     Data type representing a point in space and time. It can contain multiple values which are stored in a list.
      We don't specify a reference time yet but when we do it should probably be here
    '''

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
        # This returns a sorted tuple of coorinate names and values. It is sorted to fix an iris bug when doing
        #  linear interpolation. It's linear interpolation routine calls itself recursively and recreates the cube each time,
        #  but it doesn't seem to repopulate derived dimensions. Hence the altitude dimension (which is usually the derived one)
        #  needs to be first in the list of coordinates to interpolate over.
        return sorted([ (x, y) for x, y in self._asdict().items() if y is not None and x != 'val' ])

    def compdist(self,p1,p2):
        '''
            Compares the distance from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.haversine_dist(p1) > self.haversine_dist(p2))

    def haversine_dist(self,point2):
        '''
            Computes the Haversine distance between two points
        '''
        from jasmin_cis.utils import haversine
        return haversine(self.latitude, self.longitude, point2.latitude, point2.longitude)

    def time_sep(self,point2):
        '''
            Computes the time seperation between two points
        '''
        return abs(self.time - point2.time)

    def alt_sep(self,point2):
        '''
            Computes the height seperation between two points
        '''
        return abs(self.altitude - point2.altitude)

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


class HyperPointList(list):
    """All the functionality of a standard `list` with added "HyperPoint" context."""

    def __new__(cls, list_of_coords=None):
        """
        Given a `list` of HyperPoints, return a HyperPointList instance.

        """
        coord_list = list.__new__(cls, list_of_coords)

        # Check that all items in the incoming list are HyperPoints. Note that this checking
        # does not guarantee that a HyperPointList instance *always* has just HyperPoints in its list as
        # the append & __getitem__ methods have not been overridden.
        if not all([isinstance(coord, HyperPoint) for coord in coord_list]):
            raise ValueError('All items in list_of_coords must be Coord instances.')
        return coord_list

    @property
    def vals(self):
        return [ point.val for point in self ]