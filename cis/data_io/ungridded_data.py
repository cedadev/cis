"""
    Module for the UngriddedData class
"""
import logging
from time import gmtime, strftime
import numpy

import six
from cis.data_io.netcdf import get_data as netcdf_get_data
from cis.data_io.hdf_vd import get_data as hdf_vd_get_data
from cis.data_io.hdf_sd import get_data as hdf_sd_get_data
from cis.data_io.common_data import CommonData, CommonDataList
from cis.data_io.hyperpoint_view import UngriddedHyperPointView
from cis.data_io.write_netcdf import add_data_to_file, write_coordinates
from cis.utils import listify
import cis.maths


class Metadata(object):

    @classmethod
    def from_CubeMetadata(cls, cube_meta):
        return cls(name=cube_meta.var_name, standard_name=cube_meta.standard_name, long_name=cube_meta.long_name,
                   units=str(cube_meta.units), misc=cube_meta.attributes)

    def __init__(self, name='', standard_name='', long_name='', shape=None, units='', range=None, factor=None,
                 offset=None, missing_value=None, history='', misc=None):
        self._name = name

        self._standard_name = ''
        if standard_name:
            self.standard_name = standard_name
        elif name:
            self.standard_name = Metadata.guess_standard_name(name)

        self.long_name = long_name
        self.shape = shape

        self.units = units
        self.range = range
        self.factor = factor
        self.offset = offset
        self.missing_value = missing_value
        self.history = history
        if misc is None:
            self.misc = {}
        else:
            self.misc = misc

    def __eq__(self, other):
        result = NotImplemented

        if isinstance(other, Metadata):
            result = self._name == other._name and \
                     self._standard_name == other._standard_name and \
                     self.long_name == other.long_name and \
                     self.units == other.units
        return result

    # Must supply __ne__, Python does not defer to __eq__ for negative equality
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is not NotImplemented:
            result = not result
        return result

    # Must supply __hash__, Python 3 does not enable it if __eq__ is defined
    def __hash__(self):
        return hash(id(self))

    def summary(self, offset=5):
        """
        Creates a unicode summary of the metadata object

        :param offset: The left hand padding to apply to the text
        :return: The summary
        """
        from datetime import datetime
        string = ''
        string += '{pad:{width}}Long name = {lname}\n'.format(pad=' ', width=offset, lname=self.long_name)
        string += '{pad:{width}}Standard name = {sname}\n'.format(pad=' ', width=offset, sname=self.standard_name)
        string += '{pad:{width}}Units = {units}\n'.format(pad=' ', width=offset, units=self.units)
        string += '{pad:{width}}Missing value = {mval}\n'.format(pad=' ', width=offset, mval=self.missing_value)
        # str(tuple) returns repr(obj) on each item in the tuple, if we have a datetime tuple then we want str(obj)
        #  instead. Just make that ourselves here instead (as a str to avoid the extra quotes if we make a 'real' tuple)
        if isinstance(self.range[0], datetime):
            range_tuple = '({}, {})'.format(*self.range)
        else:
            range_tuple = self.range
        string += '{pad:{width}}Range = {range}\n'.format(pad=' ', width=offset, range=range_tuple)
        string += '{pad:{width}}History = {history}\n'.format(pad=' ', width=offset, history=self.history)
        if self.misc:
            string += '{pad:{width}}Misc attributes: \n'.format(pad=' ', width=offset)
            for k, v in self.misc.items():
                string += '{pad:{width}}{att} = {val}\n'.format(pad=' ', width=offset + 2, att=k.title(), val=v)
        return string

    def __str__(self):
        # six has a decorator for this bit, but it doesn't do errors='replace'.
        if six.PY3:
            return self.summary()
        else:
            return self.summary().encode(errors='replace')

    def __unicode__(self):
        return self.summary()

    @property
    def standard_name(self):
        return self._standard_name

    @standard_name.setter
    def standard_name(self, standard_name):
        from iris.std_names import STD_NAMES
        if standard_name is None or standard_name in STD_NAMES:
            # If the standard name is actually changing from one to another then log the fact
            if self.standard_name is not None \
                    and self.standard_name.strip() != "" \
                    and self.standard_name != standard_name:
                logging.debug("Changing standard name for dataset from '{}' to '{}'".format(self.standard_name,
                                                                                            standard_name))
            self._standard_name = standard_name
        else:
            raise ValueError('%r is not a valid standard_name' % standard_name)

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, units):
        from cf_units import Unit
        if not isinstance(units, Unit):
            try:
                # Try some basic tidying up of unit
                if isinstance(units, six.string_types):
                    if 'since' in units.lower():
                        # Often this time since epoch units are weirdly capitalised, or include extra punctuation
                        units = units.lower().replace("since:", "since").replace(",", "")
                    else:
                        # Replace number with 1 (e.g. #/cm3 == cm-3)
                        units = units.replace('#', '1')
                units = Unit(units)
            except ValueError:
                logging.info("Unable to parse cf-units: {}. Some operations may not be available.".format(units))
        self._units = units

    @staticmethod
    def guess_standard_name(name):
        standard_name = None
        if name.lower().startswith('lat'):
            standard_name = 'latitude'
        elif name.lower().startswith('lon'):
            standard_name = 'longitude'
        elif name.lower().startswith('alt') or name.lower() == 'height':
            standard_name = 'altitude'
        elif name.lower().startswith('pres') or name.lower() == 'air_pressure':
            standard_name = 'air_pressure'
        elif name.lower() == 'time':
            standard_name = 'time'
        return standard_name


# This defines the mappings for each of the ungridded data types to their reading routines, this allows 'lazy loading'
static_mappings = {"SDS": hdf_sd_get_data,
                   "HDF_SDS": hdf_sd_get_data,
                   "VDS": hdf_vd_get_data,
                   "Variable": netcdf_get_data,
                   "_Variable": netcdf_get_data}


class LazyData(object):
    """
        Wrapper (adaptor) class for the different types of possible ungridded data.
    """

    def __init__(self, data, metadata, data_retrieval_callback=None):
        """
        :param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler
        :param metadata: Any associated metadata
        :param data_retrieval_callback: An, optional, method for retrieving data when needed
        """
        from cis.exceptions import InvalidDataTypeError
        from iris.cube import CubeMetadata
        import numpy as np

        self._data_flattened = None

        self.attributes = {}

        self.metadata = Metadata.from_CubeMetadata(metadata) if isinstance(metadata, CubeMetadata) else metadata

        if isinstance(data, np.ndarray):
            # If the data input is a numpy array we can just copy it in and ignore the data_manager
            self._data = data
            self._data_manager = None
            self._post_process()
        else:
            # If the data input wasn't a numpy array we assume it is a data reference (e.g. SDS) and we refer
            #  this as a 'data manager' as it is responsible for getting the actual data.

            self._data = None
            # Although the data can be a list or a single item it's useful to cast it
            #  to a list here to make accessing it consistent
            self._data_manager = listify(data)

            if data_retrieval_callback is not None:
                # Use the given data retrieval method
                self.retrieve_raw_data = data_retrieval_callback
            elif type(self._data_manager[0]).__name__ in static_mappings and \
                    all([type(d).__name__ == type(self._data_manager[0]).__name__ for d in self._data_manager]):
                # Check that we recognise the data manager and that they are all the same

                # Set the retrieve_raw_data method to it's mapped function name
                self.retrieve_raw_data = static_mappings[type(self._data_manager[0]).__name__]
            else:
                raise InvalidDataTypeError

    def name(self, default='unknown'):
        """
        This routine returns the first name property which is not empty out of: standard_name, long_name and var_name.
        If they are all empty it returns the default string (which is 'unknown' by default).
        :return: The name of the data object as a string
        """
        return self.standard_name or self.long_name or self.var_name or default

    @property
    def shape(self):
        return self.metadata.shape

    @shape.setter
    def shape(self, shape):
        self.metadata.shape = shape

    @property
    def long_name(self):
        return self.metadata.long_name

    @long_name.setter
    def long_name(self, long_name):
        self.metadata.long_name = long_name

    @property
    def standard_name(self):
        return self.metadata.standard_name

    @standard_name.setter
    def standard_name(self, standard_name):
        self.metadata.standard_name = standard_name

    @property
    def var_name(self):
        return self.metadata._name

    @var_name.setter
    def var_name(self, var_name):
        self.metadata._name = var_name

    @property
    def units(self):
        return self.metadata.units

    @units.setter
    def units(self, units):
        self.metadata.units = units

    @property
    def data(self):
        """
        This is a getter for the data property. It caches the raw data if it has not already been read.
        Throws a MemoryError when reading for the first time if the data is too large.
        """
        import numpy.ma as ma
        if self._data is None:
            try:
                # If we were given a list of data managers then we need to concatenate them now...
                self._data = self.retrieve_raw_data(self._data_manager[0])
                if len(self._data_manager) > 1:
                    for manager in self._data_manager[1:]:
                        self._data = ma.concatenate((self._data, self.retrieve_raw_data(manager)), axis=0)
                self._post_process()
            except MemoryError:
                raise MemoryError(
                    "Failed to read the ungridded data as there was not enough memory available.\n"
                    "Consider freeing up variables or indexing the cube before getting its data.")
        return self._data

    def _post_process(self):
        """
        Perform a post-processing step on lazy loaded data
        :return: None
        """
        pass

    def __eq__(self, other):
        import numpy as np
        result = NotImplemented

        if isinstance(other, LazyData):
            # Check the metadata
            result = self.metadata == other.metadata

            # Then, if that is OK, check the data
            if result:
                result = np.allclose(self.data, other.data)

        return result

    # Must supply __ne__, Python does not defer to __eq__ for negative equality
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is not NotImplemented:
            result = not result
        return result

    # Must supply __hash__, Python 3 does not enable it if __eq__ is defined
    def __hash__(self):
        return hash(id(self))

    # Maths operator overloads
    __add__ = cis.maths.add
    __radd__ = __add__
    __sub__= cis.maths.subtract
    __mul__ = cis.maths.multiply
    __rmul__ = cis.maths.multiply
    __div__ = cis.maths.divide
    __truediv__ = cis.maths.divide
    __pow__ = cis.maths.exponentiate

    @data.setter
    def data(self, value):
        self._data = value
        self._data_flattened = None

    @property
    def data_flattened(self):
        """Returns a 1D flattened view (or copy, if necessary) of the data.
        """
        if self._data_flattened is None:
            data = self.data
            self._data_flattened = data.ravel()
        return self._data_flattened

    def add_history(self, new_history):
        """Appends to, or creates, the metadata history attribute using the supplied history string.
        The new entry is prefixed with a timestamp.

        :param new_history: history string
        """
        timestamp = strftime("%Y-%m-%dT%H:%M:%SZ ", gmtime())
        if hasattr(self.metadata, 'history') and len(self.metadata.history) > 0:
            self.metadata.history += '\n' + timestamp + new_history
        else:
            self.metadata.history = timestamp + new_history

    def add_attributes(self, attributes):
        """
        Add a variable attribute to this data

        :param attributes: Dictionary of attribute names (keys) and values.
        :return:
        """
        self.attributes.update(attributes)

    def remove_attribute(self, key):
        """
        Remove a variable attribute from this data

        :param key: Attribute key to remove
        :return:
        """
        self.attributes.pop(key, None)

    def save_data(self, output_file):
        logging.info('Saving data to %s' % output_file)
        write_coordinates(self, output_file)
        add_data_to_file(self, output_file)

    def update_shape(self, shape=None):
        if shape:
            self.metadata.shape = shape
        else:
            self.metadata.shape = self.data.shape

    def update_range(self, range=None):
        from cis.time_util import cis_standard_time_unit

        # If the user hasn't specified a range then work it out...
        if not range:
            standard_time = False
            try:
                standard_time = self.units == cis_standard_time_unit
            except ValueError:
                # If UDUNITS can't compare the units then it will raise a ValueError, in which case it's definitely not
                # our standard time
                pass

            try:
                if standard_time:
                    range = (cis_standard_time_unit.num2date(self.data.min()),
                             cis_standard_time_unit.num2date(self.data.max()))
                else:
                    range = (self.data.min(), self.data.max())
            except ValueError as e:
                # If we can't set a range for some reason then just leave it blank
                range = ()

        self.metadata.range = range

    def convert_units(self, new_units):
        """
        Convert units of LazyData object to new_units in place

        :param LazyData ug_data:
        :param cf_units.Unit or str new_units:
        :raises ValueError if new_units can't be converted to standard units, or units are incompatible
        """
        from cf_units import Unit
        if not isinstance(new_units, Unit):
            new_units = Unit(new_units)
        if not isinstance(self.units, Unit):
            # If our units aren't cf_units then they can't be...
            raise ValueError("Unable to convert non-standard LazyData units: {}".format(self.units))
        self.units.convert(self.data, new_units, inplace=True)
        self.units = new_units


class UngriddedData(LazyData, CommonData):
    """
        Wrapper (adaptor) class for the different types of possible ungridded data.
    """

    def __init__(self, data, metadata, coords, data_retrieval_callback=None):
        """
        Constructor

        :param data: The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data.
         This can be a list of data handlers, or a single data handler
        :param metadata: Any associated metadata
        :param coords: A list of the associated Coord objects
        :param data_retrieval_callback: A method for retrieving data when needed
        """
        from cis.data_io.Coord import CoordList, Coord

        if isinstance(coords, list):
            self._coords = CoordList(coords)
        elif isinstance(coords, CoordList):
            self._coords = coords
        elif isinstance(coords, Coord):
            self._coords = CoordList([coords])
        else:
            raise ValueError("Invalid Coords type")

        # TODO Find a cleaner workaround for this, for some reason UDUNITS can not parse 'per kilometer per steradian'
        if str(metadata.units) == 'per kilometer per steradian':
            metadata.units = 'kilometer^-1 steradian^-1'

        super(UngriddedData, self).__init__(data, metadata, data_retrieval_callback)

    @property
    def coords_flattened(self):
        all_coords = self.coords().find_standard_coords()
        return [(c.data_flattened if c is not None else None) for c in all_coords]

    def _post_process(self):
        """
        Perform a post processing step on lazy loaded Ungridded Data.

        :return:
        """
        # Load the data if not already loaded
        if self._data is None:
            data = self.data
        else:
            # Remove any points with missing coordinate values:
            combined_mask = numpy.zeros(self._data.shape, dtype=bool).flatten()
            for coord in self._coords:
                combined_mask |= numpy.ma.getmaskarray(coord.data).flatten()
                if coord.data.dtype != 'object':
                    combined_mask |= numpy.isnan(coord.data).flatten()
                coord.update_shape()
                coord.update_range()
            if combined_mask.any():
                n_points = numpy.count_nonzero(combined_mask)
                logging.warning(
                    "Identified {n_points} point(s) which were missing values for some or all coordinates - "
                    "these points have been removed from the data.".format(n_points=n_points))
                for coord in self._coords:
                    coord.data = numpy.ma.masked_array(coord.data.flatten(), mask=combined_mask).compressed()
                    coord.update_shape()
                    coord.update_range()
                if numpy.ma.is_masked(self._data):
                    new_data_mask = numpy.ma.masked_array(self._data.mask.flatten(), mask=combined_mask).compressed()
                    new_data = numpy.ma.masked_array(self._data.data.flatten(), mask=combined_mask).compressed()
                    self._data = numpy.ma.masked_array(new_data, mask=new_data_mask)
                else:
                    self._data = numpy.ma.masked_array(self._data.flatten(), mask=combined_mask).compressed()
            self.update_shape()
            self.update_range()

    def make_new_with_same_coordinates(self, data=None, var_name=None, standard_name=None,
                                       long_name=None, history=None, units=None, flatten=False):
        """
        Create a new, empty UngriddedData object with the same coordinates as this one.

        :param data: Data to use (if None then defaults to all zeros)
        :param var_name: Variable name
        :param standard_name: Variable CF standard name
        :param long_name: Variable long name
        :param history: Data history string
        :param units: Variable units
        :param flatten: Whether to flatten the data and coordinates (for ungridded data only)
        :return: UngriddedData instance
        """
        if data is None:
            data = numpy.zeros(self.shape)
        metadata = Metadata(name=var_name, standard_name=standard_name,
                            long_name=long_name, history='', units=units)
        if flatten:
            from cis.data_io.Coord import Coord
            data = data.flatten()
            new_coords = []
            for coord in self._coords:
                new_coords.append(Coord(coord.data_flattened, coord.metadata, coord.axis))
        else:
            new_coords = self._coords
        ug_data = UngriddedData(data=data, metadata=metadata, coords=new_coords)
        # Copy the history in separately so it gets the timestamp added.
        if history:
            ug_data.add_history(history)
        return ug_data

    def __getitem__(self, keys):
        """
        Return a COPY of the data with the given slice. We copy to emulate the Iris Cube behaviour
        """
        from copy import deepcopy
        # Create a copy of the slice of each of the coords
        new_coords = []
        for c in self.coords():
            new_coords.append(c[keys])
        # The data is just a new LazyData objects with the sliced data. Note this is a slice of the whole (concatenated)
        #  data, and will lead to post-processing before slicing.
        # TODO: We could be cleverer and figure out the right slice across the various data managers to only read the
        #  right data from disk.
        return UngriddedData(data=self.data[keys].copy(), metadata=deepcopy(self.metadata), coords=new_coords)

    def copy(self, data=None):
        """
        Create a copy of this UngriddedData object with new data and coordinates
        so that that they can be modified without held references being affected.
        Will call any lazy loading methods in the data and coordinates

        :param ndarray data: Replace the data of the ungridded data copy with provided data

        :return: Copied UngriddedData object
        """
        from copy import deepcopy
        data = data if data is not None else numpy.ma.copy(self.data)  # This will load the data if lazy load
        coords = self.coords().copy()
        return UngriddedData(data=data, metadata=deepcopy(self.metadata), coords=coords)

    @property
    def size(self):
        return self.data.size

    def count(self):
        return self.data.count() if hasattr(self.data, 'count') else self.data.size

    @property
    def history(self):
        return self.metadata.history

    @property
    def x(self):
        return self.coord(axis='X')

    @property
    def y(self):
        return self.coord(axis='Y')

    @property
    def lat(self):
        return self.coord(standard_name='latitude')

    @property
    def lon(self):
        return self.coord(standard_name='longitude')

    @property
    def time(self):
        return self.coord(standard_name='time')

    def hyper_point(self, index):
        """
        :param index: The index in the array to find the point for
        :return: A hyperpoint representing the data at that point
        """
        from cis.data_io.hyperpoint import HyperPoint
        return HyperPoint(self.coord(standard_name='latitude').data.flat[index],
                          self.coord(standard_name='longitude').data.flat[index],
                          self.coord(standard_name='altitude').data.flat[index],
                          self.coord(standard_name='time').data.flat[index],
                          self.coord(standard_name='air_pressure').data.flat[index],
                          self.data.flat[index])

    def as_data_frame(self, copy=True, time_index=True, name=None):
        """
        Convert an UngriddedData object to a Pandas DataFrame.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
        """
        df = _coords_as_data_frame(self.coords(), time_index=time_index)
        try:
            df[name or self.name()] = _to_flat_ndarray(self.data, copy)
        except ValueError:
            logging.warn("Copy created of MaskedArray for {} when creating Pandas DataFrame".format(self.name()))
            df[name or self.name()] = _to_flat_ndarray(self.data, True)

        return df

    def coords(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, var_name=None,
               dim_coords=True):
        """
        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        self._post_process()
        return self._coords.get_coords(name_or_coord, standard_name, long_name, attributes, axis, var_name)

    def coord(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, var_name=None):
        """
        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as :meth:`coords`.
        """
        return self.coords().get_coord(name_or_coord, standard_name, long_name, attributes, axis, var_name)

    def get_coordinates_points(self):
        """Returns a HyperPointView of the coordinates of points.

        :return: HyperPointView of the coordinates of points
        """
        return UngriddedHyperPointView(self.coords_flattened, None)

    def get_all_points(self):
        """Returns a HyperPointView of the points.

        :return: HyperPointView of all the data points
        """
        return UngriddedHyperPointView(self.coords_flattened, self.data_flattened)

    def get_non_masked_points(self):
        """Returns a HyperPointView for which the default iterator omits masked points.

        :return: HyperPointView of the data points
        """
        return UngriddedHyperPointView(self.coords_flattened, self.data_flattened, non_masked_iteration=True)

    def find_standard_coords(self):
        """Constructs a list of the standard coordinates.
        The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
        list in this order.

        :return: list of coordinates or None if coordinate not present
        """
        return self.coords().find_standard_coords()

    @property
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        return False

    @classmethod
    def from_points_array(cls, hyperpoints):
        """
        Constuctor for building an UngriddedData object from a list of hyper points

        :param hyperpoints: list of HyperPoints
        """
        from cis.data_io.Coord import Coord, CoordList
        from cis.data_io.hyperpoint import HyperPointList
        from cis.time_util import cis_standard_time_unit

        if not isinstance(hyperpoints, HyperPointList):
            hyperpoints = HyperPointList(hyperpoints)

        values = hyperpoints.vals
        latitude = hyperpoints.latitudes
        longitude = hyperpoints.longitudes
        air_pressure = hyperpoints.air_pressures
        altitude = hyperpoints.altitudes
        time = hyperpoints.times

        coord_list = []
        if latitude is not None:
            coord_list.append(Coord(latitude, Metadata(standard_name='latitude', units='degrees north')))
        if longitude is not None:
            coord_list.append(Coord(longitude, Metadata(standard_name='longitude', units='degrees east')))
        if air_pressure is not None:
            coord_list.append(Coord(air_pressure, Metadata(standard_name='air_pressure', units='Pa')))
        if altitude is not None:
            coord_list.append(Coord(altitude, Metadata(standard_name='altitude', units='meters')))
        if time is not None:
            coord_list.append(Coord(time, Metadata(standard_name='time', units=cis_standard_time_unit)))
        coords = CoordList(coord_list)

        return cls(values, Metadata(), coords)

    def summary(self, shorten=False):
        """
        Unicode summary of the UngriddedData with metadata of itself and its coordinates
        """
        summary = 'Ungridded data: {name} / ({units}) \n'.format(name=self.name(), units=self.units)
        if shorten:
            return summary

        summary += '     Shape = {}\n'.format(self.data.shape) + '\n'
        summary += '     Total number of points = {}\n'.format(self.size)
        summary += '     Number of non-masked points = {}\n'.format(self.count())

        summary += str(self.metadata)

        summary += '     Coordinates: \n'
        for c in self.coords():
            summary += '{pad:{width}}{name}\n'.format(pad=' ', width=7, name=c.name())
            c.update_range()
            summary += c.metadata.summary(offset=10)

        return summary

    def __repr__(self):
        return "<cis 'UngriddedData' of %s>" % self.summary(shorten=True)

    def __str__(self):
        # six has a decorator for this bit, but it doesn't do errors='replace'.
        if six.PY3:
            return self.summary()
        else:
            return self.summary().encode(errors='replace')

    def __unicode__(self):
        return self.summary()

    def set_longitude_range(self, range_start):
        """
        Rotates the longitude coordinate array and changes its values by
        360 as necessary to force the values to be within a 360 range starting
        at the specified value.
        :param range_start: starting value of required longitude range
        """
        from cis.utils import fix_longitude_range
        self.coord(standard_name='longitude').data = fix_longitude_range(self.lon.points, range_start)

    def subset(self, **kwargs):
        """
        Subset the data based on the specified constraints. Note that the limits are inclusive.

        The subset region is defined by passing keyword arguments for each dimension to be subset over, each argument
        must be a slice, or have two entries (a maximum and a minimum). Datetime objects can be used to specify upper
        and lower datetime limits, or a single PartialDateTime object can be used to specify a datetime range.

        The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
        axis and var_name.

        For example:
            data.subset(x=[0, 80], y=slice(10, 50))

        or:
            data.aggregate(t=PartialDateTime(2008,9))


        A shape keyword can also be supplied as a WKT string or shapely object to subset in lat/lon by an arbitrary
        shape. In this case the lat/lon bounds are taken as the bounding box of the shape.

        :param kwargs: The constraints for each coordinate dimension
        :return CommonData:
        """
        from cis.subsetting.subset import subset, UngriddedSubsetConstraint
        return subset(self, UngriddedSubsetConstraint, **kwargs)

    def aggregate(self, how=None, **kwargs):
        """
        Aggregate the UngriddedData object based on the specified grids. The grid is defined by passing keyword
        arguments for each dimension, each argument must be a slice, or have three entries (a maximum, a minimum and a
        gridstep). The default aggregation method ('moments') returns the mean, standard deviation and number of points
         as separate GriddedData objects.

        Datetime objects can be used to specify upper and lower datetime limits, or a
        single PartialDateTime object can be used to specify a datetime range. The gridstep can be specified as a
        DateTimeDelta object.

        The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
        axis and var_name.

        For example:
            data.aggregate(x=[-180, 180, 360], y=slice(-90, 90, 10))

        or:
            data.aggregate(how='mean', t=[PartialDateTime(2008,9), timedelta(days=1))

        :param str how: The kernel to use in the aggregation (moments, mean, min, etc...). Default is moments
        :param kwargs: The grid specifications for each coordinate dimension
        :return GriddedData:
        """
        agg = _aggregate_ungridded(self, how, **kwargs)
        # Return the single item if there's only one (this depends on the kernel used)
        if len(agg) == 1:
            agg = agg[0]
        return agg

    def sampled_from(self, data, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                     var_name='', var_long_name='', var_units='', **kwargs):
        """
        Collocate the CommonData object with another CommonData object using the specified collocator and kernel

        :param CommonData or CommonDataList data: The data to resample
        :param str how: Collocation method (e.g. lin, nn, bin or box)
        :param str or cis.collocation.col_framework.Kernel kernel:
        :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
        :param float fill_value: Value to use for missing data
        :param str var_name: The output variable name
        :param str var_long_name: The output variable's long name
        :param str var_units: The output variable's units
        :return CommonData: The collocated dataset
        """
        return _ungridded_sampled_from(self, data, how=how, kernel=kernel,
                                       missing_data_for_missing_sample=missing_data_for_missing_sample,
                                       fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                       var_units=var_units, **kwargs)

    def _get_default_plot_type(self, lat_lon=False):
        if lat_lon:
            return 'scatter2d'
        else:
            return 'line'


class UngriddedCoordinates(CommonData):
    """
    Wrapper (adaptor) class for the different types of possible ungridded data.
    """

    def __init__(self, coords):
        """
        Constructor

        :param coords: A list of the associated Coord objects
        """
        from cis.data_io.Coord import CoordList, Coord

        if isinstance(coords, list):
            self._coords = CoordList(coords)
        elif isinstance(coords, CoordList):
            self._coords = coords
        elif isinstance(coords, Coord):
            self._coords = CoordList([coords])
        else:
            raise ValueError("Invalid Coords type")
        self._post_process()

    def _post_process(self):
        """
        Perform a post processing step on lazy loaded Coordinate Data

        :return:
        """
        # Remove any points with missing coordinate values:
        combined_mask = numpy.zeros(self._coords[0].data_flattened.shape, dtype=bool)
        for coord in self._coords:
            combined_mask |= numpy.ma.getmaskarray(coord.data_flattened)
            if coord.data.dtype != 'object':
                combined_mask |= numpy.isnan(coord.data).flatten()
        if combined_mask.any():
            n_points = numpy.count_nonzero(combined_mask)
            logging.warning("Identified {n_points} point(s) which were missing values for some or all coordinates - "
                            "these points have been removed from the data.".format(n_points=n_points))
            for coord in self._coords:
                coord.data = numpy.ma.masked_array(coord.data_flattened, mask=combined_mask).compressed()
                coord.update_shape()
                coord.update_range()

    @property
    def coords_flattened(self):
        all_coords = self.coords().find_standard_coords()
        return [(c.data_flattened if c is not None else None) for c in all_coords]

    @property
    def history(self):
        return "UngriddedCoordinates have no history"

    @property
    def size(self):
        if len(self._coords) > 1:
            return self._coords[0].data.size
        else:
            return 0

    def count(self):
        # There can be no masked coordinate points
        return self.size

    @property
    def x(self):
        return self.coord(axis='X')

    @property
    def y(self):
        return self.coord(axis='Y')

    @property
    def lat(self):
        return self.coord(standard_name='latitude')

    @property
    def lon(self):
        return self.coord(standard_name='longitude')

    @property
    def time(self):
        return self.coord(standard_name='time')

    @property
    def var_name(self):
        return ''

    def hyper_point(self, index):
        """
        :param index: The index in the array to find the point for
        :return: A hyperpoint representing the data at that point
        """
        from cis.data_io.hyperpoint import HyperPoint
        return HyperPoint(self.coord(standard_name='latitude').data.flat[index],
                          self.coord(standard_name='longitude').data.flat[index],
                          self.coord(standard_name='altitude').data.flat[index],
                          self.coord(standard_name='time').data.flat[index],
                          self.coord(standard_name='air_pressure').data.flat[index],
                          None)

    def as_data_frame(self, copy=True, time_index=True, name=None):
        """
        Convert an UngriddedCoordinates object to a Pandas DataFrame.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
        """
        return _coords_as_data_frame(self._coords, time_index=time_index)

    def coords(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, var_name=None,
               dim_coords=True):
        """
        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        return self._coords.get_coords(name_or_coord, standard_name, long_name, attributes, axis, var_name)

    def coord(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, var_name=None):
        """
        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as :meth:`coords`.

        """
        return self._coords.get_coord(name_or_coord, standard_name, long_name, attributes, axis, var_name)

    def get_coordinates_points(self):
        return UngriddedHyperPointView(self.coords_flattened, None)

    def get_all_points(self):
        """Returns a HyperPointView of the points.

        :return: HyperPointView of all the data points
        """
        return UngriddedHyperPointView(self.coords_flattened, None)

    def get_non_masked_points(self):
        """Returns a HyperPointView for which the default iterator omits masked points.

        :return: HyperPointView of the data points
        """
        return UngriddedHyperPointView(self.coords_flattened, None, non_masked_iteration=True)

    @property
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        return False

    def set_longitude_range(self, range_start):
        """
        Rotates the longitude coordinate array and changes its values by
        360 as necessary to force the values to be within a 360 range starting
        at the specified value.
        :param range_start: starting value of required longitude range
        """
        from cis.utils import fix_longitude_range
        self.coord(standard_name='longitude').data = fix_longitude_range(self.lon.points, range_start)

    def subset(self, **kwargs):
        raise NotImplementedError("Subset is not available for UngriddedCoordinates objects")

    def collocated_onto(self, sample, how='', kernel=None, **kwargs):
        raise NotImplementedError("UngriddedCoordinates objects cannot be used as sources of data for collocation.")

    def sampled_from(self, data, how='', kernel=None, missing_data_for_missing_sample=False, fill_value=None,
                     var_name='', var_long_name='', var_units='', **kwargs):
        """
        Collocate the CommonData object with another CommonData object using the specified collocator and kernel

        Note - that the default value for missing_data_for_missing_sample is different in this implementation as
        compared to the UngriddedData implementation.

        :param CommonData or CommonDataList data: The data to resample
        :param str how: Collocation method (e.g. lin, nn, bin or box)
        :param str or cis.collocation.col_framework.Kernel kernel:
        :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
        :param float fill_value: Value to use for missing data
        :param str var_name: The output variable name
        :param str var_long_name: The output variable's long name
        :param str var_units: The output variable's units
        :return CommonData: The collocated dataset
        """
        return _ungridded_sampled_from(self, data, how=how, kernel=kernel,
                                       missing_data_for_missing_sample=missing_data_for_missing_sample,
                                       fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                       var_units=var_units, **kwargs)

    def _get_default_plot_type(self, lat_lon=False):
        raise NotImplementedError("UngriddedCoordinates have no default plot type")

    def var_name(self):
        raise NotImplementedError("UngriddedCoordinates have no var name")


class UngriddedDataList(CommonDataList):
    """
    Class which represents multiple UngriddedData objects (e.g. from reading multiple variables)
    """

    def __str__(self):
        return "UngriddedDataList: \n%s" % super(UngriddedDataList, self).__str__()

    @property
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        return False

    def save_data(self, output_file):
        """
        Save the UngriddedDataList to a file

        :param output_file: output filename
        :return:
        """
        logging.info('Saving data to %s' % output_file)
        # Should only write coordinates out once
        write_coordinates(self[0], output_file)
        for data in self:
            add_data_to_file(data, output_file)

    def get_non_masked_points(self):
        """
        Returns a list containing a HyperPointViews for which the default iterator omits masked points, for each item in
        this UngriddedDataList.

        :return: List of HyperPointViews of the data points
        """
        points_list = []
        for data in self:
            points_list.append(data.get_non_masked_points())
        return points_list

    def coord(self, *args, **kwargs):
        """
        Call :func:`UnGriddedData.coord(*args, **kwargs)` for the first item of data (assumes all data in list has
        same coordinates)

        :param args:
        :param kwargs:
        :return:
        """
        return self[0].coord(*args, **kwargs)

    def copy(self):
        """
        Create a copy of this UngriddedDataList with new data and coordinates
        so that that they can be modified without held references being affected.
        Will call any lazy loading methods in the data and coordinates

        :return: Copied UngriddedData object
        """
        output = UngriddedDataList()
        for variable in self:
            output.append(variable.copy())
        return output

    def as_data_frame(self, copy=True):
        """
        Convert an UngriddedDataList object to a Pandas DataFrame. Note that UngriddedDataList objects are expected to
        share coordinates, so only the coordinates from the first object in the list are used.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.

        .. note::
            This function will copy your data by default.
            If you have a large array that cannot be copied,
            make sure it is not masked and use copy=False.
        """
        import numpy as np

        df = self[0].as_data_frame(copy=copy)

        for d in self[1:]:
            try:
                data = _to_flat_ndarray(d.data, copy)
            except ValueError:
                logging.warn("Copy created of MaskedArray for {} when creating Pandas DataFrame".format(d.name()))
                data = _to_flat_ndarray(d.data, True)
            df[d.name()] = data

        return df

    def subset(self, **kwargs):
        from cis.subsetting.subset import subset, UngriddedSubsetConstraint
        return subset(self, UngriddedSubsetConstraint, **kwargs)

    def aggregate(self, how='', **kwargs):
        """
        Aggregate the UngriddedDataList object based on the specified grids. The grid is defined by passing keyword
        arguments for each dimension, each argument must be a slice, or have three entries (a maximum, a minimum and a
        gridstep). The default aggregation method ('moments') returns the mean, standard deviation and number of points
         as separate GriddedData objects (for each UngriddedData object in the list).

        Datetime objects can be used to specify upper and lower datetime limits, or a
        single PartialDateTime object can be used to specify a datetime range. The gridstep can be specified as a
        DateTimeDelta object.

        The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
        axis and var_name.

        For example:
            data.aggregate(x=[-180, 180, 360], y=slice(-90, 90, 10))

        or:
            data.aggregate(how='mean', t=[PartialDateTime(2008,9), timedelta(days=1))

        :param str how: The kernel to use in the aggregation (moments, mean, min, etc...)
        :param kwargs: The grid specifications for each coordinate dimension
        :return GriddedDataList:
        """
        return _aggregate_ungridded(self, how, **kwargs)


def _coords_as_data_frame(coord_list, copy=True, time_index=True):
    """
    Convert a CoordList object to a Pandas DataFrame.

    :param copy: Create a copy of the data for the new DataFrame? Default is True.
    :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
    """
    import pandas as pd
    from cis.time_util import cis_standard_time_unit
    from cf_units import Unit

    columns = {}
    time = None

    for coord in coord_list.get_coords():
        try:
            data = _to_flat_ndarray(coord.data, copy)
        except ValueError:
            logging.warn("Copy created of MaskedArray for {} when creating Pandas DataFrame".format(coord.name()))
            data = _to_flat_ndarray(coord.data, True)

        if time_index and coord.standard_name == 'time':
            if str(coord.units).lower() == 'datetime object':
                time = data
            elif isinstance(coord.units, Unit):
                time = coord.units.num2date(data)
            else:
                time = cis_standard_time_unit.num2date(data)
        else:
            columns[coord.standard_name] = data

    return pd.DataFrame(columns, index=time)


def _to_flat_ndarray(data, copy=True):
    """
    Convert a (possibly masked) numpy array into its flat equivalent, with or without copying it.

    :param data:
    :param copy:
    :return:
    """
    import numpy as np

    if isinstance(data, np.ma.MaskedArray):
        if not copy:
            raise ValueError("Masked arrays must always be copied.")
        # We need to cast the array to a float so that we can fill the array with NaNs for Pandas (which would do the
        #  same trick itself anyway)
        ndarr = data.astype(float).filled(np.NaN).flatten()
    elif copy:
        ndarr = data.flatten()
    else:
        ndarr = data.ravel()

    return ndarr


def _ungridded_sampled_from(sample, data, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                            var_name='', var_long_name='', var_units='', **kwargs):
    """
    Collocate the CommonData object with another CommonData object using the specified collocator and kernel

    :param CommonData or CommonDataList data: The data to resample
    :param str how: Collocation method (e.g. lin, nn, bin or box)
    :param str or cis.collocation.col_framework.Kernel kernel:
    :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
    :param float fill_value: Value to use for missing data
    :param str var_name: The output variable name
    :param str var_long_name: The output variable's long name
    :param str var_units: The output variable's units
    :return CommonData: The collocated dataset
    """
    from cis.collocation import col_implementations as ci
    from cis.data_io.gridded_data import GriddedData, GriddedDataList
    from cis.collocation.col import collocate, get_kernel

    if isinstance(data, UngriddedData) or isinstance(data, UngriddedDataList):
        col = ci.GeneralUngriddedCollocator(fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                            var_units=var_units,
                                            missing_data_for_missing_sample=missing_data_for_missing_sample)

        # Box is the default, and only option for ungridded -> ungridded collocation
        if how not in ['', 'box']:
            raise ValueError("Invalid method specified for ungridded -> ungridded collocation: " + how)
        con = ci.SepConstraintKdtree(**kwargs)
        # We can have any kernel, default to moments
        kernel = get_kernel(kernel)
    elif isinstance(data, GriddedData) or isinstance(data, GriddedDataList):
        col = ci.GriddedUngriddedCollocator(fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                            var_units=var_units,
                                            missing_data_for_missing_sample=missing_data_for_missing_sample)
        con = None
        if how not in ['', 'lin', 'nn']:
            raise ValueError("Invalid method specified for gridded -> ungridded collocation: " + how)

        kernel = how or 'lin'
    else:
        raise ValueError("Invalid argument, data must be either GriddedData or UngriddedData")

    return collocate(data, sample, col, con, kernel)


def _aggregate_ungridded(data, how, **kwargs):
    """
    Aggregate an UngriddedData or UngriddedDataList based on the specified grids
    :param UngriddedData or UngriddedDataList data: The data object to aggregate
    :param cis.collocation.col_framework.Kernel kernel: The kernel to use in the aggregation
    :param kwargs: The grid specifications for each coordinate dimension
    :return:
    """
    from cis.aggregation.ungridded_aggregator import UngriddedAggregator
    from cis.collocation.col import get_kernel
    from cis.time_util import PartialDateTime
    from datetime import datetime, timedelta
    from cis import __version__

    kernel = get_kernel(how)
    grid_spec = {}
    for dim_name, grid in kwargs.items():
        c = data._get_coord(dim_name)
        if all(hasattr(grid, att) for att in ('start', 'stop', 'step')):
            g = grid
        elif len(grid) == 2 and isinstance(grid[0], PartialDateTime):
            g = slice(grid[0].min(), grid[0].max(), grid[1])
        elif len(grid) == 3:
            g = slice(grid[0], grid[1], grid[2])
        else:
            raise ValueError("Invalid subset arguments: {}".format(grid))

        # Fill in defaults
        grid_start = g.start if g.start is not None else c.points.min()
        if isinstance(grid_start, datetime):
            grid_start = c.units.date2num(grid_start)

        grid_end = g.stop if g.stop is not None else c.points.max()
        if isinstance(grid_end, datetime):
            grid_end = c.units.date2num(grid_end)

        if g.step is None:
            raise ValueError("Grid step must not be None")
        else:
            grid_step = g.step

        if isinstance(grid_step, timedelta):
            # Standard time is days since, so turn this into a fractional number of days
            grid_step = grid_step.total_seconds() / (24*60*60)

        grid_spec[c.name()] = slice(grid_start, grid_end, grid_step)

    # We have to make the history before doing the aggregation as the grid dims get popped-off during the operation
    history = "Aggregated using CIS version " + __version__ + \
              "\n variables: " + str(getattr(data, "var_name", "Unknown")) + \
              "\n from files: " + str(getattr(data, "filenames", "Unknown")) + \
              "\n using new grid: " + str(grid_spec) + \
              "\n with kernel: " + str(kernel) + "."

    aggregator = UngriddedAggregator(grid_spec)
    data = aggregator.aggregate(data, kernel)

    data.add_history(history)

    return data
