"""
    Module for the UngriddedData class
"""
import logging
from time import gmtime, strftime
import numpy

from cis import utils
from cis.data_io.netcdf import get_data as netcdf_get_data
from cis.data_io.hdf_vd import get_data as hdf_vd_get_data
from cis.data_io.hdf_sd import get_data as hdf_sd_get_data
from cis.data_io.common_data import CommonData, CommonDataList
from cis.data_io.hyperpoint_view import UngriddedHyperPointView
from cis.data_io.write_netcdf import add_data_to_file, write_coordinates
from cis.utils import listify


class Metadata(object):
    @classmethod
    def from_CubeMetadata(cls, cube_meta):
        return cls(name=cube_meta.var_name, standard_name=cube_meta.standard_name, long_name=cube_meta.long_name,
                   units=str(cube_meta.units), misc=cube_meta.attributes)

    def __init__(self, name='', standard_name='', long_name='', shape='', units='', range='', factor='', offset='',
                 missing_value='', calendar='', history='', misc=None):
        self._name = name
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
        self.calendar = calendar
        self.history = history
        if misc is None:
            self.misc = {}
        else:
            self.misc = misc

    def summary(self, offset=5):
        """
        Creates a unicode summary of the metadata object

        :param offset: The left hand padding to apply to the text
        :return: The summary
        """
        string = ''
        string += '{pad:{width}}Long name = {lname}\n'.format(pad=' ', width=offset, lname=self.long_name)
        string += '{pad:{width}}Standard name = {sname}\n'.format(pad=' ', width=offset, sname=self.standard_name)
        string += '{pad:{width}}Units = {units}\n'.format(pad=' ', width=offset, units=self.units)
        if self.calendar:
            string += '{pad:{width}}Calendar = {cal}\n'.format(pad=' ', width=offset, cal=self.calendar)
        string += '{pad:{width}}Missing value = {mval}\n'.format(pad=' ', width=offset, mval=self.missing_value)
        string += '{pad:{width}}Range = {range}\n'.format(pad=' ', width=offset, range=self.range)
        string += '{pad:{width}}History = {history}\n'.format(pad=' ', width=offset, history=self.history)
        if self.misc:
            string += '{pad:{width}}Misc attributes: \n'.format(pad=' ', width=offset)
            for k, v in self.misc.items():
                string += '{pad:{width}}{att} = {val}\n'.format(pad=' ', width=offset + 2, att=k.title(), val=v)
        return string

    def __str__(self):
        return self.summary().encode(errors='replace')

    def __unicode__(self):
        return self.summary()

    def alter_standard_name(self, new_standard_name):
        """
        Alter the standard name and log an info line to say this is happening if the standard name is not empty.
        Also changes internal name for metadata or the same.

        :param new_standard_name:
        """
        if self.standard_name is not None \
                and self.standard_name.strip() is not "" \
                and self.standard_name != new_standard_name:
            logging.info("Changing standard name for dataset from '{}' to '{}'"
                         .format(self.standard_name, new_standard_name))
        self.standard_name = new_standard_name

        if self._name is not None \
                and self._name.strip() is not "" \
                and self._name != new_standard_name:
            logging.info("Changing variable name for dataset from '{}' to '{}'"
                         .format(self._name, new_standard_name))
        self._name = new_standard_name

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

    def name(self):
        """
        This routine returns the first name property which is not empty out of: _name, standard_name and long_name.
        If they are all empty it returns an empty string
        :return: The name of the data object as a string
        """

        for name in [self.metadata._name, self.metadata.standard_name, self.metadata.long_name]:
            if name:
                return name
        return ''

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

    def copy_metadata_from(self, other_data):
        """
        Method to copy the metadata from one UngriddedData/Cube object to another
        """
        self._coords = other_data.coords()
        self.metadata = other_data._metadata

        # def __getitem__(self, item): pass
        # This method could be overridden to provide the ability to ask for slices of data
        #  e.g. UngridedDataObject[012:32.4:5]

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
                    range = (str(cis_standard_time_unit.num2date(self.data.min())),
                             str(cis_standard_time_unit.num2date(self.data.max())))
                else:
                    range = (self.data.min(), self.data.max())
            except ValueError as e:
                # If we can't set a range for some reason then just leave it blank
                range = ()

        self.metadata.range = str(range)


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

    def copy(self):
        """
        Create a copy of this UngriddedData object with new data and coordinates
        so that that they can be modified without held references being affected.
        Will call any lazy loading methods in the data and coordinates

        :return: Copied UngriddedData object
        """
        data = numpy.ma.copy(self.data)  # This will load the data if lazy load
        coords = self.coords().copy()
        return UngriddedData(data=data, metadata=self.metadata, coords=coords)

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

    def as_data_frame(self, copy=True):
        """
        Convert an UngriddedData object to a Pandas DataFrame.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
        """
        df = _coords_as_data_frame(self.coords())
        try:
            df[self.name()] = _to_flat_ndarray(self.data, copy)
        except ValueError:
            logging.warn("Copy created of MaskedArray for {} when creating Pandas DataFrame".format(self.name()))
            df[self.name()] = _to_flat_ndarray(self.data, True)

        return df

    def coords(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, dim_coords=True):
        """
        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        self._post_process()
        return self._coords.get_coords(name_or_coord, standard_name, long_name, attributes, axis)

    def coord(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as :meth:`coords`.
        """
        return self.coords().get_coord(name_or_coord, standard_name, long_name, attributes, axis)

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
            coord_list.append(Coord(time, Metadata(standard_name='time', units='seconds')))
        coords = CoordList(coord_list)

        return cls(values, Metadata(), coords)

    def summary(self):
        """
        Unicode summary of the UngriddedData with metadata of itself and its coordinates
        """
        summary = 'Ungridded data: {name} / ({units}) \n'.format(name=self.name(), units=self.units)
        summary += '     Shape = {}\n'.format(self.data.shape) + '\n'
        summary += '     Total number of points = {}\n'.format(self.data.size)
        num_non_masked_points = self.data.count() if hasattr(self.data, 'count') else self.data.size
        summary += '     Number of non-masked points = {}\n'.format(num_non_masked_points)

        summary += str(self.metadata)

        summary += '     Coordinates: \n'
        for c in self.coords():
            summary += '{pad:{width}}{name}\n'.format(pad=' ', width=7, name=c.name())
            c.update_range()
            summary += c.metadata.summary(offset=10)

        return summary

    def __str__(self):
        return self.summary().encode(errors='replace')

    def __unicode__(self):
        return self.summary()

    def subset(self, **kwargs):
        """
        Subset the CommonData object based on the specified constraints
        :param kwargs:
        :return:
        """
        from cis.subsetting.subset import subset, UngriddedSubsetConstraint
        return subset(self, UngriddedSubsetConstraint, **kwargs)

    def aggregate(self, kernel=None, **kwargs):
        """
        Aggregate the CommonData object based on the specified grids
        :param cis.collocation.col_framework.Kernel kernel: The kernel to use in the aggregation
        :param kwargs: The grid specifications for each coordinate dimension
        :return:
        """
        _aggregate_ungridded(self, kernel, **kwargs)


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
        all_coords = self._coords.find_standard_coords()
        self.coords_flattened = [(c.data_flattened if c is not None else None) for c in all_coords]

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
    def history(self):
        return "UngriddedCoordinates have no history"

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

    def as_data_frame(self, copy=True):
        """
        Convert an UngriddedCoordinates object to a Pandas DataFrame.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
        """
        return _coords_as_data_frame(self._coords)

    def coords(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None, dim_coords=True):
        """
        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        return self._coords.get_coords(name_or_coord, standard_name, long_name, attributes, axis)

    def coord(self, name_or_coord=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as :meth:`coords`.

        """
        return self._coords.get_coord(name_or_coord, standard_name, long_name, attributes, axis)

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

    def subset(self, **kwargs):
        raise NotImplementedError("Subset is not available for UngriddedCoordinates objects")

    def aggregate(self, **kwargs):
        raise NotImplementedError("Aggregation is not available for UngriddedCoordinates objects")

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
        _ungridded_sampled_from(self, data, how=how, kernel=kernel,
                                missing_data_for_missing_sample=missing_data_for_missing_sample,
                                fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                var_units=var_units, **kwargs)


class UngriddedDataList(CommonDataList):
    """
    Class which represents multiple UngriddedData objects (e.g. from reading multiple variables)
    """

    def __str__(self):
        "<UngriddedDataList: %s>" % super(UngriddedDataList, self).__str__()

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

    def aggregate(self, kernel=None, **kwargs):
        """
        Aggregate based on the specified grids
        :param cis.collocation.col_framework.Kernel kernel: The kernel to use in the aggregation
        :param kwargs: The grid specifications for each coordinate dimension
        :return:
        """
        return _aggregate_ungridded(self, kernel, **kwargs)


def _coords_as_data_frame(coord_list, copy=True):
    """
    Convert a CoordList object to a Pandas DataFrame.

    :param copy: Create a copy of the data for the new DataFrame? Default is True.
    :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
    """
    import pandas as pd
    from cis.time_util import cis_standard_time_unit

    columns = {}
    time = None

    for coord in coord_list.get_coords():
        try:
            data = _to_flat_ndarray(coord.data, copy)
        except ValueError:
            logging.warn("Copy created of MaskedArray for {} when creating Pandas DataFrame".format(coord.name()))
            data = _to_flat_ndarray(coord.data, True)

        if coord.standard_name == 'time':
            if coord.units.lower() == 'datetime object':
                time = data
            else:
                time = cis_standard_time_unit.num2date(data)
        else:
            columns[coord.name()] = data

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
        ndarr = data.astype(np.float64).filled(np.NaN).flatten()
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

    col = ci.GeneralUngriddedCollocator(fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                        var_units=var_units,
                                        missing_data_for_missing_sample=missing_data_for_missing_sample)

    if isinstance(data, UngriddedData) or isinstance(data, UngriddedDataList):
        # Box is the default, and only option for ungridded -> ungridded collocation
        if how != '' or how != 'box':
            raise ValueError("Invalid method specified for ungridded -> ungridded collocation: " + how)
        con = ci.SepConstraintKdtree(**kwargs)
        # We can have any kernel, default to moments
        kernel = get_kernel(kernel)
    elif isinstance(data, GriddedData) or isinstance(data, GriddedDataList):
        # nn is the default for gridded -> ungridded collocation
        if how == '' or how == 'nn':
            con = None
            kernel = ci.nn_gridded()
        elif how == 'lin':
            con = None
            kernel = ci.li()
        elif how == 'box':
            con = ci.SepConstraintKdtree(**kwargs)
            # We can have any kernel, default to moments
            kernel = get_kernel(kernel)
        else:
            raise ValueError("Invalid method specified for gridded -> ungridded collocation: " + how)
    else:
        raise ValueError("Invalid argument, data must be either GriddedData or UngriddedData")

    return collocate(data, sample, col, con, kernel)


def _aggregate_ungridded(data, kernel, **kwargs):
    """
    Aggregate an UngriddedData or UngriddedDataList based on the specified grids
    :param UngriddedData or UngriddedDataList data: The data object to aggregate
    :param cis.collocation.col_framework.Kernel kernel: The kernel to use in the aggregation
    :param kwargs: The grid specifications for each coordinate dimension
    :return:
    """
    from cis.aggregation.ungridded_aggregator import UngriddedAggregator
    from cis.aggregation.aggregate import aggregate
    from cis.collocation.col import get_kernel
    return aggregate(UngriddedAggregator, data, get_kernel(kernel), **kwargs)