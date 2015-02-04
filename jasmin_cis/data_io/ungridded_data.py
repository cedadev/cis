'''
    Module for the UngriddedData class
'''
import logging
from time import gmtime, strftime

from netCDF4 import _Variable, Variable
from pyhdf.SD import SDS
import numpy

from jasmin_cis import utils
from jasmin_cis.data_io.netcdf import get_data as netcdf_get_data
from jasmin_cis.data_io.hdf_vd import get_data as hdf_vd_get_data, VDS
from jasmin_cis.data_io.hdf_sd import get_data as hdf_sd_get_data, HDF_SDS
from jasmin_cis.data_io.common_data import CommonData, CommonDataList
from jasmin_cis.data_io.hyperpoint_view import UngriddedHyperPointView
from jasmin_cis.data_io.write_netcdf import add_data_to_file, write_coordinates


class Metadata(object):

    @classmethod
    def from_CubeMetadata(cls, cube_meta):
        return cls(name=cube_meta.var_name,standard_name=cube_meta.standard_name,long_name=cube_meta.long_name, units=str(cube_meta.units), misc=cube_meta.attributes)


    def __init__(self, name='', standard_name='', long_name='', shape='', units='', range='', factor='', offset='', missing_value='', calendar='', history = '', misc=None):
        self._name = name
        if standard_name:
            self.standard_name = standard_name
        else:
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

    def alter_standard_name(self, new_standard_name):
        """
        Alter the standard name and log an info line to say this is happening if the standard name is not empty
        Also changes internal name for metadata
        or the same
        :param new_standard_name:
        :return: nothing
        """
        if self.standard_name is not None \
                and self.standard_name.strip() is not "" \
                and self.standard_name != new_standard_name:
            logging.info("Changing standard name for dataset from '{}' to '{}'"
                         .format(self.standard_name, new_standard_name))
        self.standard_name = new_standard_name
        self._name = new_standard_name

    @staticmethod
    def guess_standard_name(name):
        standard_name = name
        if name.lower().startswith('lat'):
            standard_name = 'latitude'
        elif name.lower().startswith('lon'):
            standard_name = 'longitude'
        elif name.lower().startswith('alt') or name.lower() == 'height':
            standard_name = 'altitude'
        elif name.lower().startswith('pres'):
            standard_name = 'air_pressure'
        return standard_name


# This defines the mappings for each of the ungridded data types to their reading routines, this allows 'lazy loading'
static_mappings = {SDS: hdf_sd_get_data,
                   HDF_SDS: hdf_sd_get_data,
                   VDS: hdf_vd_get_data,
                   Variable: netcdf_get_data,
                   _Variable: netcdf_get_data}


class LazyData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    def __init__(self, data, metadata, data_retrieval_callback=None):
        '''
        :param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler
        :param metadata: Any associated metadata
        :param data_retrieval_callback: An, optional, method for retrieving data when needed
        '''
        from jasmin_cis.exceptions import InvalidDataTypeError
        from iris.cube import CubeMetadata
        import numpy as np

        self._data_flattened = None

        self.metadata = Metadata.from_CubeMetadata(metadata) if isinstance(metadata, CubeMetadata) else metadata

        if isinstance(data, np.ndarray):
            # If the data input is a numpy array we can just copy it in and ignore the data_manager
            self._data = data
            self._data_manager = None
        else:
            # If the data input wasn't a numpy array we assume it is a data reference (e.g. SDS) and we refer
            #  this as a 'data manager' as it is responsible for getting the actual data.

            self._data = None
            # Although the data can be a list or a single item it's useful to cast it
            #  to a list here to make accessing it consistent
            if isinstance(data, list):
                self._data_manager = data
            else:
                self._data_manager = [ data ]

            if data_retrieval_callback is not None:
                # Use the given data retrieval method
                self.retrieve_raw_data = data_retrieval_callback
            elif self._data_manager[0].__class__ in static_mappings and all([d.__class__ == self._data_manager[0].__class__ for d in self._data_manager ]) :
                # Check that we recognise the data manager and that they are all the same

                # Set the retrieve_raw_data method to it's mapped function name
                self.retrieve_raw_data = static_mappings[self._data_manager[0].__class__]
            else:
                raise InvalidDataTypeError

    def name(self):
        """
            This routine returns the first name property which is not empty out of: _name, standard_name and long_name
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
        '''
            This is a getter for the data property. It caches the raw data if it has not already been read.
             Throws a MemoryError when reading for the first time if the data is too large.
        '''
        import numpy.ma as ma
        if self._data is None:
            try:
                # If we ere given a list of data managers then we need to concatenate them now...
                self._data=self.retrieve_raw_data(self._data_manager[0])
                if len(self._data_manager) > 1:
                    for manager in self._data_manager[1:]:
                        self._data = ma.concatenate((self._data,self.retrieve_raw_data(manager)),axis=0)
            except MemoryError:
                raise MemoryError(
                    "Failed to read the ungridded data as there was not enough memory available.\n"
                    "Consider freeing up variables or indexing the cube before getting its data.")
        return self._data

    @data.setter
    def data(self, value):
        # TODO remove this - it's only for testing colocation at the moment
        self._data = value

    @property
    def data_flattened(self):
        '''Returns a 1D flattened view (or copy, if necessary) of the data.
        '''
        if self._data_flattened is None:
            data = self.data
            self._data_flattened = data.ravel()
        return self._data_flattened

    def copy_metadata_from(self, other_data):
        '''
            Method to copy the metadata from one UngriddedData/Cube object to another
        '''
        self._coords = other_data.coords()
        self.metadata = other_data._metadata

        #def __getitem__(self, item): pass
        # This method can be overridden to provide the ability to ask for slices of data e.g. UngridedDataObject[012:32.4:5]
        # Actually implementing it would be very tricky as you have to keep track of the data and the coordinates without
        #  necessarily actually reading them

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

    def save_data(self, output_file):
        output_file = utils.add_file_prefix('cis-', output_file)
        logging.info('Saving data to %s' % output_file)
        write_coordinates(self, output_file)
        add_data_to_file(self, output_file)


class UngriddedData(LazyData, CommonData):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    def __init__(self, data, metadata, coords, data_retrieval_callback=None):
        '''
        Constructor

        :param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler
        :param metadata: Any associated metadata
        :param coords: A list of the associated Coord objects
        :param data_retrieval_callback: A method for retrieving data when needed
        '''
        from jasmin_cis.data_io.Coord import CoordList, Coord

        super(UngriddedData, self).__init__(data, metadata, data_retrieval_callback)

        if isinstance(coords, list):
            self._coords = CoordList(coords)
        elif isinstance(coords, CoordList):
            self._coords = coords
        elif isinstance(coords, Coord):
            self._coords = CoordList([coords])
        else:
            raise ValueError("Invalid Coords type")
        all_coords = self._coords.find_standard_coords()
        self.coords_flattened = [(c.data_flattened if c is not None else None) for c in all_coords]

        #TODO Find a cleaner workaround for this, for some reason UDUNITS can not parse 'per kilometer per steradian'
        if str(metadata.units) == 'per kilometer per steradian':
            metadata.units = 'kilometer^-1 steradian^-1'

    def make_new_with_same_coordinates(self, data=None, var_name=None, standard_name=None,
                                       long_name=None, history=None, units=None):
        """
        Create a new, empty GriddedData object with the same coordinates as this one
        :param data: Data to use (if None then defaults to all zeros)
        :param var_name: Variable name
        :param standard_name: Variable CF standard name
        :param long_name: Variable long name
        :param history: Data history string
        :param units: Variable units
        :return: GriddedData instance
        """
        if data is None:
            data = numpy.zeros(self.shape)
        metadata = Metadata(name=var_name, standard_name=standard_name,
                            long_name=long_name, history='', units=units)
        data = UngriddedData(data=data, metadata=metadata, coords=self._coords)
        # Copy the history in separately so it gets the timestamp added.
        data.add_history(history)
        return data

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

    def hyper_point(self, index):
        """

        :param index: The index in the array to find the point for
        :return: A hyperpoint representing the data at that point
        """
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        return HyperPoint(self.coord(standard_name='latitude').data.flat[index],
                          self.coord(standard_name='longitude').data.flat[index],
                          self.coord(standard_name='altitude').data.flat[index],
                          self.coord(standard_name='time').data.flat[index],
                          self.coord(standard_name='air_pressure').data.flat[index],
                          self.data.flat[index])

    def coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None, dim_coords=True):
        """

        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        return self._coords.get_coords(name, standard_name, long_name, attributes, axis)

    def coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """

        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as L(coords).

        """
        return self._coords.get_coord(name, standard_name, long_name, attributes, axis)

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
        return self._coords.find_standard_coords()

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
        from jasmin_cis.data_io.Coord import Coord, CoordList
        from jasmin_cis.data_io.hyperpoint import HyperPointList

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


class UngriddedCoordinates(CommonData):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    def __init__(self, coords):
        '''
        Constructor

        :param coords: A list of the associated Coord objects
        '''
        from jasmin_cis.data_io.Coord import CoordList, Coord

        if isinstance(coords, list):
            self._coords = CoordList(coords)
        elif isinstance(coords, CoordList):
            self._coords = coords
        elif isinstance(coords, Coord):
            self._coords = CoordList([coords])
        else:
            raise ValueError("Invalid Coords type")
        all_coords = self._coords.find_standard_coords()
        self.coords_flattened = [(c.data_flattened if c is not None else None) for c in all_coords]

    @property
    def history(self):
        """
        Return the associated
        :return:
        """
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

    def hyper_point(self, index):
        """

        :param index: The index in the array to find the point for
        :return: A hyperpoint representing the data at that point
        """
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        return HyperPoint(self.coord(standard_name='latitude').data.flat[index],
                          self.coord(standard_name='longitude').data.flat[index],
                          self.coord(standard_name='altitude').data.flat[index],
                          self.coord(standard_name='time').data.flat[index],
                          self.coord(standard_name='air_pressure').data.flat[index],
                          None)

    def coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None, dim_coords=True):
        """

        :return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        return self._coords.get_coords(name, standard_name, long_name, attributes, axis)

    def coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """

        :raise: CoordinateNotFoundError
        :return: A single coord given the same arguments as L(coords).

        """
        return self._coords.get_coord(name, standard_name, long_name, attributes, axis)

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
        output_file = utils.add_file_prefix('cis-', output_file)
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