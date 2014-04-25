from collections import namedtuple
import datetime
from jasmin_cis.time_util import convert_datetime_to_std_time


class HyperPoint(namedtuple('HyperPoint', ['latitude', 'longitude', 'altitude', 'air_pressure', 'time', 'val'])):
    '''
     Data type representing a point in space and time. It can contain multiple values which are stored in a list.
      We don't specify a reference time yet but when we do it should probably be here
    '''
    standard_names = ['latitude', 'longitude', 'altitude', 'air_pressure', 'time']
    number_standard_names = len(standard_names)
    LATITUDE = 0
    LONGITUDE = 1
    ALTITUDE = 2
    AIR_PRESSURE = 3
    TIME = 4
    VAL = 5

    def __new__(cls, lat=None, lon=None, alt=None, pres=None, t=None, val=None):
        '''
            Small constructor for the HyperPoint named tuple to allow optional arguments
             and set-up value list.
        '''

        # If no value was specified create an empty list, otherwise create a list with one entry
        if val is None or val == []:
            val = []
        else:
            val = [ val ]

        # If t was given as a datetime we need to convert it into our standard time
        if isinstance(t,datetime.datetime):
            t = convert_datetime_to_std_time(t)

        point = super(HyperPoint, cls).__new__(cls, lat, lon, alt, pres, t, val)

        # Store the coordinate tuple for this point in case we need it later
        point.coord_tuple = point.get_coord_tuple()

        return point

    def modified(self, lat=None, lon=None, alt=None, pres=None, t=None, val=None):
        """Creates a HyperPoint with modified values.

        :param lat:
        :param lon:
        :param alt:
        :param pres:
        :param t:
        :param val:
        :return:
        """
        values = [v for v in self]
        if lat is not None:
            values[HyperPoint.LATITUDE] = lat
        if lon is not None:
            values[HyperPoint.LONGITUDE] = lon
        if alt is not None:
            values[HyperPoint.ALTITUDE] = alt
        if pres is not None:
            values[HyperPoint.AIR_PRESSURE] = pres
        if t is not None:
            if isinstance(t, datetime.datetime):
                values[HyperPoint.TIME] = convert_datetime_to_std_time(t)
        if val is not None:
            if val == []:
                values[HyperPoint.VAL] = []
            else:
                values[HyperPoint.VAL] = [val]
        point = super(HyperPoint, self).__new__(HyperPoint, *values)
        point.coord_tuple = point.get_coord_tuple()
        return point

    def same_point_in_time(self, other):
        return self.time == other.time

    def same_point_in_space(self, other):
        return ( self.latitude == other.latitude and self.longitude == other.longitude and
                 self.altitude == other.altitude and self.air_pressure == other.air_pressure )

    def same_point_in_space_and_time(self, other):
        return ( self.same_point_in_space(other) and self.same_point_in_time(other) )

    def get_coord_tuple(self):
        # This returns a sorted tuple of coordinate names and values. It is sorted to fix an iris bug when doing
        #  linear interpolation. It's linear interpolation routine calls itself recursively and recreates the cube each time,
        #  but it doesn't seem to repopulate derived dimensions. Hence the altitude dimension (which is usually the derived one)
        #  needs to be first in the list of coordinates to interpolate over.
        return sorted([ (x, y) for x, y in self._asdict().items() if y is not None and x != 'val' ])

    def compdist(self,p1,p2):
        '''
            Compares the distance from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.haversine_dist(p1) > self.haversine_dist(p2))

    def compalt(self,p1,p2):
        '''
            Compares the distance from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.alt_sep(p1) > self.alt_sep(p2))

    def comppres(self,p1,p2):
        '''
            Compares the pressure from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.pres_sep(p1) > self.pres_sep(p2))

    def comptime(self,p1,p2):
        '''
            Compares the distance from this point to p1 and p2. Returns True if p2 is closer to self than p1
        '''
        return (self.time_sep(p1) > self.time_sep(p2))

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

    def pres_sep(self,point2):
        '''
            Computes the pressure ratio between two points, this is always >= 1.
        '''
        if self.air_pressure > point2.air_pressure:
            return self.air_pressure / point2.air_pressure
        else:
            return point2.air_pressure / self.air_pressure

    def furthest_point_from(self):
        '''
            Return a point on the opposite side of the globe from this point
        '''
        furthest_lat = -self.latitude
        if self.longitude > 180:
            furthest_lon = self.longitude - 180.0
        else:
            furthest_lon = self.longitude + 180.0
        return HyperPoint(furthest_lat, furthest_lon, self.altitude, self.air_pressure, self.time, self.val)


class HyperPointList(list):
    """All the functionality of a standard `list` with added "HyperPoint" context."""

    def __new__(cls, list_of_points=None):
        """
        Given a `list` of HyperPoints, return a HyperPointList instance. This checks that all of the items in the list
         are HyperPoint instances but no other checks. Specifically each Hyper point should have the same shape, that is
         if any point has a coordinate as None, then no other points should have a value for that coordinate. This is not
         imposed here because of the potential overhead but it is assumed by other functions in CIS.

        """
        point_list = list.__new__(cls, list_of_points)

        # Check that all items in the incoming list are HyperPoints. Note that this checking
        # does not guarantee that a HyperPointList instance *always* has just HyperPoints in its list as
        # the append & __getitem__ methods have not been overridden.
        #TODO In fact it doesn't even check here because the list is not initialised yet. Override __init__ for
        # mutable objects.
        if not all([isinstance(point, HyperPoint) for point in point_list]):
            raise ValueError('All items in list_of_coords must be Coord instances.')
        return point_list

    def enumerate_non_masked_points(self):
        for idx, point in enumerate(self):
            yield idx, point

    @property
    def vals(self):
        from numpy import zeros
        n_points = len(self)

        values = zeros(n_points)
        for i, point in enumerate(self):
            try:
                values[i] = point.val[0]
            except IndexError:
                pass

        return values

    @property
    def longitudes(self):
        from numpy import zeros

        if self[0].longitude is not None:
            n_points = len(self)

            values = zeros(n_points)
            for i, point in enumerate(self):
                values[i] = point.longitude
        else:
            values = None
        return values

    @property
    def latitudes(self):
        from numpy import zeros

        if self[0].latitude is not None:
            n_points = len(self)

            values = zeros(n_points)
            for i, point in enumerate(self):
                values[i] = point.latitude
        else:
            values = None
        return values

    @property
    def air_pressures(self):
        from numpy import zeros

        if self[0].air_pressure is not None:
            n_points = len(self)

            values = zeros(n_points)
            for i, point in enumerate(self):
                values[i] = point.air_pressure
        else:
            values = None
        return values

    @property
    def altitudes(self):
        from numpy import zeros

        if self[0].altitude is not None:
            n_points = len(self)

            values = zeros(n_points)
            for i, point in enumerate(self):
                values[i] = point.altitude
        else:
            values = None
        return values

    @property
    def times(self):
        from numpy import zeros

        if self[0].time is not None:
            n_points = len(self)

            values = zeros(n_points)
            for i, point in enumerate(self):
                values[i] = point.time
        else:
            values = None
        return values
