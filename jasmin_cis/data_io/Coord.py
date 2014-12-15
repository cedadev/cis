import logging, collections
from jasmin_cis.data_io.hyperpoint import HyperPoint
from jasmin_cis.data_io.hyperpoint_view import UngriddedHyperPointView
from jasmin_cis.data_io.ungridded_data import LazyData

class Coord(LazyData):

    def __init__(self, data, metadata, axis=''):
        """

        :param data:
        :param metadata:
        :param axis: A string label for the axis, e.g. 'X', 'Y', 'Z', or 'T'
        :return:
        """
        super(Coord, self).__init__(data, metadata)
        self.axis = axis.upper()
        # Fix an issue where IRIS cannot parse units 'deg' (should be degrees).
        if self.units == 'deg':
            self.units = 'degrees'


    @property
    def points(self):
        """Alias for data to match iris.coords.Coord.points
        :return: coordinate data
        """
        return self.data

    def __eq__(self, other):
        return other.metadata.standard_name == self.metadata.standard_name and self.metadata.standard_name != ''

    def convert_julian_to_std_time(self, calender='standard'):
        from jasmin_cis.time_util import convert_julian_date_to_std_time_array, cis_standard_time_unit
        #if not self.units.startswith("Julian Date"): raise ValueError("Time units must be Julian Date for conversion to an Object")
        self._data = convert_julian_date_to_std_time_array(self.data, calender)
        self.units = str(cis_standard_time_unit)
        self.metadata.calendar = cis_standard_time_unit.calendar

    def convert_TAI_time_to_std_time(self, ref):
        from jasmin_cis.time_util import convert_sec_since_to_std_time_array, cis_standard_time_unit
        self._data = convert_sec_since_to_std_time_array(self.data, ref)
        self.units = str(cis_standard_time_unit)
        self.metadata.calendar = cis_standard_time_unit.calendar

    def convert_to_std_time(self, time_stamp_info=None):
        """
        Convert this coordinate to standard time. It will use:
         the units of the coordinate if it is in the standard x since x
         the first word of the units combined with the time stamp (if the timestamp is not given an error is thrown)
        :param time_stamp_info: the time stamp info from the file, None if it does not exist
        :return: nothing
        """
        from jasmin_cis.time_util import convert_time_since_to_std_time, cis_standard_time_unit, \
            convert_time_using_time_stamp_info_to_std_time

        if "since" in self.units:
            self._data = convert_time_since_to_std_time(self.data, self.units)
        else:
            if time_stamp_info is None:
                raise ValueError("File must have time stamp info if converting without 'since' in units definition")
            self._data = convert_time_using_time_stamp_info_to_std_time(self.data, self.units, time_stamp_info)

        self.units = str(cis_standard_time_unit)
        self.metadata.calendar = cis_standard_time_unit.calendar

    def convert_datetime_to_standard_time(self):
        from jasmin_cis.time_util import convert_obj_to_standard_date_array, cis_standard_time_unit
        self._data = convert_obj_to_standard_date_array(self.data)
        self.units = str(cis_standard_time_unit)
        self.metadata.calendar = cis_standard_time_unit.calendar


class CoordList(list):
    """All the functionality of a standard `list` with added "Coord" context."""

    def __init__(self, *args):
        """
        Given a `list` of Coords, return a CoordList instance.

        :param list_of_coords: list of coordinates with which to initialise the list
        """
        list.__init__(self, *args)

        # Check that all items in the incoming list are coords. Note that this checking
        # does not guarantee that a CoordList instance *always* has just coords in its list as
        # the append & __getitem__ methods have not been overridden.
        if not all([isinstance(coord, Coord) for coord in self]):
            raise ValueError('All items in list_of_coords must be Coord instances.')

    def append(self, other):
        """
            Safely add a new coordinate object to the list, this checks for a unique axis and standard_name
        :param other: Other coord to add
        :raise: DuplicateCoordinateError
        :return:
        """
        from jasmin_cis.exceptions import DuplicateCoordinateError
        if any([ other == item for item in self ]):
            raise DuplicateCoordinateError()
        super(CoordList, self).append(other)

    def get_coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a list of coordinates in this UngriddedData object fitting the given criteria. This is deliberately very
         similar to Cube.coords() to maintain a similar interface and because the functionality is similar. There
          is no distrinction between dimension coordinates and auxilliary coordinates here though.

        :param name:  The standard name or long name or default name of the desired coordinate.
            If None, does not check for name. Also see, :attr:`Cube.name`.
        :param standard_name: The CF standard name of the desired coordinate. If None, does not check for standard name.
        :param long_name: An unconstrained description of the coordinate. If None, does not check for long_name.
        :param attributes: A dictionary of attributes desired on the coordinates. If None, does not check for attributes.
        :param axis: The desired coordinate axis, see :func:`iris.util.guess_coord_axis`. If None, does not check for axis.
            Accepts the values 'X', 'Y', 'Z' and 'T' (case-insensitive).

        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        from collections import Mapping
        coords = self

        if name is not None:
            coords = filter(lambda coord_: coord_.name() == name, coords)

        if standard_name is not None:
            coords = filter(lambda coord_: coord_.standard_name == standard_name, coords)

        if long_name is not None:
            coords = filter(lambda coord_: coord_.long_name == long_name, coords)

        if axis is not None:
            axis = axis.upper()
            coords = filter(lambda coord_: coord_.axis == axis, coords)

        if attributes is not None:
            if not isinstance(attributes, Mapping):
                raise ValueError('The attributes keyword was expecting a dictionary type, but got a %s instead.' % type(attributes))
            filter_func = lambda coord_: all(k in coord_.attributes and coord_.attributes[k] == v for k, v in attributes.iteritems())
            coords = filter(filter_func, coords)

        return coords

    def get_coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a single coord given the same arguments as L(coords). If the arguments given do not result in precisely
         1 coordinate being matched, a CoordinateNotFoundError is raised.

        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as L(coords).

        """
        from jasmin_cis.exceptions import CoordinateNotFoundError
        coords = self.get_coords(name=name, standard_name=standard_name, long_name=long_name, attributes=attributes, axis=axis)
        if len(coords) == 0:  # If we found none by name, try with standard name only
            coords = self.get_coords(standard_name=name)

        if len(coords) > 1:
            msg = 'Expected to find exactly 1 coordinate, but found %s. They were: %s.'\
                  % (len(coords), ', '.join(coord.name() for coord in coords))
            raise CoordinateNotFoundError(msg)
        elif len(coords) == 0:
            bad_name = name or standard_name or long_name or axis or ''
            msg = 'Expected to find exactly 1 %s coordinate, but found none.' % bad_name
            raise CoordinateNotFoundError(msg)

        return coords[0]

    def get_coordinates_points(self):
        all_coords = self.find_standard_coords()
        flattened_coords = [(c.data_flattened if c is not None else None) for c in all_coords]
        return UngriddedHyperPointView(flattened_coords, None)

    def get_standard_coords(self, data_len):
        """Constructs a list of the standard coordinate values.
        The standard coordinates are latitude, longitude, altitude, time and air_pressure; they occur in the return
        list in this order.
        :param data_len: expected length of coordinate data
        :return: list of indexed sequences of coordinate values
        """
        from jasmin_cis.exceptions import CoordinateNotFoundError

        empty_data = [None for i in xrange(data_len)]
        ret_list = []

        for name in HyperPoint.standard_names:
            try:
                coord = self.get_coord(standard_name=name).data.flatten()
            except CoordinateNotFoundError:
                coord = empty_data
            ret_list.append(coord)

        return ret_list

    def find_standard_coords(self):
        """Constructs a list of the standard coordinates.
        The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
        list in this order.
        :return: list of coordinates or None if coordinate not present
        """
        from jasmin_cis.exceptions import CoordinateNotFoundError

        ret_list = []

        for name in HyperPoint.standard_names:
            try:
                coord = self.get_coord(standard_name=name)
            except CoordinateNotFoundError:
                coord = None
            ret_list.append(coord)

        return ret_list
