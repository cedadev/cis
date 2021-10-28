import numpy
from cis.data_io.hyperpoint import HyperPoint
from cis.data_io.hyperpoint_view import UngriddedHyperPointView
from cis.data_io.ungridded_data import LazyData
from cis.utils import fix_longitude_range


class Coord(LazyData):
    @classmethod
    def from_many_coordinates(cls, coords):
        """
        Create a single coordinate object from the concatenation of all of the coordinate objects in the input list,
        updating the shape as appropriate

        :param coords: A list of coordinate objects to be combined
        :return: A single :class:`Coord` object
        """
        from cis.utils import concatenate
        data = concatenate([ug.data for ug in coords])
        metadata = coords[0].metadata  # Use the first file as a master for the metadata...
        metadata.shape = data.shape  # But update the shape
        return cls(data, metadata, coords[0].axis)

    def __init__(self, data, metadata, axis='', data_retrieval_callback=None):
        """

        :param data:
        :param metadata:
        :param axis: A string label for the axis, e.g. 'X', 'Y', 'Z', or 'T'
        :return:
        """
        super(Coord, self).__init__(data, metadata, data_retrieval_callback)
        self.axis = axis.upper()
        # Fix an issue where cf_units cannot parse units 'deg' (should be degrees).
        if isinstance(self.units, str) and self.units == 'deg':
            self.units = 'degrees'

    def __getitem__(self, keys):
        """
        Return a COPY of the Coord with the given slice. We copy to emulate the Iris Cube behaviour
        """
        from copy import deepcopy
        # The data is just a new LazyData objects with the sliced data. Note this is a slice of the whole (concatenated)
        #  data, and will lead to post-processing before slicing.
        # TODO: We could be cleverer and figure out the right slice across the various data managers to only read the
        #  right data from disk.
        return Coord(self.data[keys].copy(), metadata=deepcopy(self.metadata), axis=self.axis)

    @property
    def points(self):
        """Alias for :func:`self.data`, to match :func:`iris.coords.Coord.points` interface

        :return: Coordinate data values
        """
        return self.data

    def __eq__(self, other):
        return other.metadata.standard_name == self.metadata.standard_name and self.metadata.standard_name != ''

    def convert_julian_to_std_time(self):
        from cis.time_util import convert_julian_date_to_std_time, cis_standard_time_unit
        # if not self.units.startswith("Julian Date"):
        #     raise ValueError("Time units must be Julian Date for conversion to an Object")
        self._data = convert_julian_date_to_std_time(self.data)
        self.units = cis_standard_time_unit

    def convert_TAI_time_to_std_time(self, ref):
        from cis.time_util import convert_sec_since_to_std_time, cis_standard_time_unit
        self._data = convert_sec_since_to_std_time(self.data, ref)
        self.units = cis_standard_time_unit

    def convert_to_std_time(self, time_stamp_info=None):
        """
        Convert this coordinate to standard time. It will use either: the units of the coordinate if it is a cf_units
        Unit, or the first word of the units, combined with the time stamp (if the timestamp is not given an error is
        thrown).

        :param time_stamp_info: the time stamp info from the file, None if it does not exist
        """
        from cis.time_util import convert_time_since_to_std_time, cis_standard_time_unit, \
            convert_time_using_time_stamp_info_to_std_time, convert_datetime_to_std_time
        from cf_units import Unit

        if isinstance(self.units, Unit):
            self._data = convert_time_since_to_std_time(self.data, self.units)
        elif str(self.units).lower().startswith('datetime'):
            self._data = convert_datetime_to_std_time(self.data)
        else:
            if time_stamp_info is None:
                raise ValueError("File must have time stamp info if converting without 'since' in units definition")
            self._data = convert_time_using_time_stamp_info_to_std_time(self.data, self.units, time_stamp_info)

        self.units = cis_standard_time_unit

    def convert_datetime_to_standard_time(self):
        from cis.time_util import convert_datetime_to_std_time, cis_standard_time_unit
        self._data = convert_datetime_to_std_time(self.data)
        self.units = cis_standard_time_unit

    def convert_standard_time_to_datetime(self):
        from cis.time_util import convert_std_time_to_datetime, cis_standard_time_unit
        if self.units == cis_standard_time_unit:
            self.data = convert_std_time_to_datetime(self.data)
            self.units = "DateTime Object"

    def set_longitude_range(self, range_start):
        """
        Confine the coordinate longitude range to 360 degrees from the :attr:`range_start` value.

        :param float range_start: Start of the longitude range
        """
        self._data = fix_longitude_range(self._data, range_start)
        self._data_flattened = None

    def copy(self, data=None):
        """
        Create a copy of this Coord object with new data so that that they can be modified without held references
        being affected. This will call any lazy loading methods in the coordinate data

        :return: Copied :class:`Coord`
        """
        from copy import deepcopy
        data = data if data is not None else numpy.ma.copy(self.data)  # Will call lazy load method
        return Coord(data, deepcopy(self.metadata), axis=deepcopy(self.axis))


class CoordList(list):
    """All the functionality of a standard :class:`list` with added :class:`Coord` context."""

    def __init__(self, *args):
        """ Given many :class:`Coord`s, return a :class:`CoordList` instance. """
        list.__init__(self, *args)

        # Check that all items in the incoming list are coords. Note that this checking
        # does not guarantee that a CoordList instance *always* has just coords in its list as
        # the append & __getitem__ methods have not been overridden.
        if not all([isinstance(coord, Coord) for coord in self]):
            raise ValueError('All items in list_of_coords must be Coord instances.')

    def append(self, other):
        """
        Safely add a new coordinate object to the list, this checks for a unique :attr:`axis` and :attr:`standard_name`.

        :param :class:`Coord` other: Other coord to add
        :raises DuplicateCoordinateError: If the coordinate is not unique in the list
        """
        from cis.exceptions import DuplicateCoordinateError
        if any([other == item for item in self]):
            raise DuplicateCoordinateError()
        super(CoordList, self).append(other)

    def get_coords(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None,
                   var_name=None):
        """
        Return a list of coordinates in this :class:`CoordList` fitting the given criteria. This is deliberately very
        similar to :func:`Cube.coords()` to maintain a similar interface and because the functionality is similar. There
        is no distinction between dimension coordinates and auxiliary coordinates here though.

        :param name_or_coord: This should be either: The standard name or long name or default name of the desired
         coordinate; Or, a :class:`Coord` instance whose metadata should be used for the search criteria (note that
         currently only the standard name is compared). If None, does not check for name. Also see, :attr:`Cube.name`.
        :type name: string or None or :class:`Coord`
        :param standard_name: The CF standard name of the desired coordinate. If None, does not check for standard name.
        :type standard_name: string or None
        :param long_name: An unconstrained description of the coordinate. If None, does not check for long_name.
        :type long_name: string or None
        :param attributes: A dictionary of attributes desired on the coordinates. If None, does not check for attributes
        :type attributes: dict or None
        :param axis: The desired coordinate axis, see :func:`iris.util.guess_coord_axis`. If None, does not check for
         axis. Accepts the values 'X', 'Y', 'Z' and 'T' (case-insensitive).
        :type axis: string or None
        :param var_name: The name of the variable which the coordinate was read from. If None, does not check for long_name.
        :type var_name: string or None

        :return: A :class:`CoordList` of coordinates fitting the given criteria
        """
        import six
        from collections.abc import Mapping
        coords = self

        if isinstance(name_or_coord, six.string_types):
            name = name_or_coord
            coord = None
        else:
            name = None
            coord = name_or_coord

        if name is not None:
            coords = [coord_ for coord_ in coords if coord_.name() == name]

        if standard_name is not None:
            coords = [coord_ for coord_ in coords if coord_.standard_name == standard_name]

        if long_name is not None:
            coords = [coord_ for coord_ in coords if coord_.long_name == long_name]

        if axis is not None:
            axis = axis.upper()
            coords = [coord_ for coord_ in coords if coord_.axis == axis]

        if var_name is not None:
            coords = [coord_ for coord_ in coords if coord_.var_name == var_name]

        if attributes is not None:
            if not isinstance(attributes, Mapping):
                raise ValueError(
                    'The attributes keyword was expecting a dictionary type, but got a %s instead.' % type(attributes))
            coords = [coord_ for coord_ in coords if all(
                            k in coord_.attributes and coord_.attributes[k] == v for k, v in attributes.items())]

        if coord is not None:
            coords = [coord_ for coord_ in coords if coord_ == coord]

        return coords

    def get_coord(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None,
                  var_name=None):
        """
        Return a single coord fitting the given criteria. This is deliberately very
        similar to :func:`Cube.coord()` method to maintain a similar interface and because the functionality is similar.
        There is no distinction between dimension coordinates and auxilliary coordinates here though.

        :param name_or_coord: This should be either: The standard name or long name or default name of the desired
         coordinate; Or, a :class:`Coord` instance whose metadata should be used for the search criteria (note that
         currently only the standard name is compared). If None, does not check for name. Also see, :attr:`Cube.name`.
        :type name: string or None or :class:`Coord`
        :param standard_name: The CF standard name of the desired coordinate. If None, does not check for standard name.
        :type standard_name: string or None
        :param long_name: An unconstrained description of the coordinate. If None, does not check for long_name.
        :type long_name: string or None
        :param attributes: A dictionary of attributes desired on the coordinates. If None, does not check for attributes
        :type attributes: dict or None
        :param axis: The desired coordinate axis, see :func:`iris.util.guess_coord_axis`. If None, does not check for
         axis. Accepts the values 'X', 'Y', 'Z' and 'T' (case-insensitive).
        :type axis: string or None
        :param var_name: The name of the variable which the coordinate was read from. If None, does not check for long_name.
        :type var_name: string or None

        :raises CoordinateNotFoundError: If the arguments given do not result in precisely
         1 coordinate being matched.
        :return: A single :class:`Coord`.

        """
        from cis.exceptions import CoordinateNotFoundError
        coords = self.get_coords(name_or_coord=name_or_coord, standard_name=standard_name, long_name=long_name,
                                 attributes=attributes, axis=axis, var_name=var_name)
        if len(coords) == 0:  # If we found none by name, try with standard name only
            coords = self.get_coords(standard_name=name_or_coord)

        if len(coords) > 1:
            msg = 'Expected to find exactly 1 coordinate, but found %s. They were: %s.' \
                  % (len(coords), ', '.join(coord.name() for coord in coords))
            raise CoordinateNotFoundError(msg)
        elif len(coords) == 0:
            bad_name = str(name_or_coord) or standard_name or long_name or axis or ''
            msg = 'Expected to find exactly 1 %s coordinate, but found none.' % bad_name
            raise CoordinateNotFoundError(msg)

        return coords[0]

    def get_coordinates_points(self):
        all_coords = self.find_standard_coords()
        flattened_coords = [(c.data_flattened if c is not None else None) for c in all_coords]
        return UngriddedHyperPointView(flattened_coords, None)

    def find_standard_coords(self):
        """Constructs a list of the standard coordinates.
        The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
        list in this order.

        :return: :class:`list` of coordinates or None if coordinate not present
        """
        from cis.exceptions import CoordinateNotFoundError

        ret_list = []

        for name in HyperPoint.standard_names:
            try:
                coord = self.get_coord(standard_name=name)
            except CoordinateNotFoundError:
                coord = None
            ret_list.append(coord)

        return ret_list

    def copy(self):
        """
        Create a copy of this CoordList object with new data so that that they can
        be modified without held references being affected. This will call any lazy loading methods in the coordinate
        data

        :return: Copied :class:`CoordList`
        """
        copied = CoordList()
        for coord in self:
            copied.append(coord.copy())
        return copied
