'''
    Module for the UngriddedData class
'''
from collections import namedtuple
from numpy import shape
import data_io.netcdf
import hdf_vd
import hdf_sd
import netcdf

class Metadata(object):

    def __init__(self, name='', long_name='', shape='', units='', range='', factor='', offset='', missing_value='', misc=None):
        self.name = name
        self.long_name = long_name
        self.shape = shape
        self.units = units
        self.range = range
        self.factor = factor
        self.offset = offset
        self.missing_value = missing_value
        if misc is None:
            self.misc = {}
        else:
            self.misc = misc

    def copy_attributes_into(self, obj):
        obj.__dict__.update(self.__dict__)


# Remove the metadata method which removes the need for the first mapping below - this should come straight in with
#  the data. Also we don't need the data type - we can work it out by mapping on class type

# Define the vars of the methods that must be mapped to, these are the methods UngriddedData objects will call
#  I think this could actually define the EXTERNAL interface without creating any sub methods in the UngriddedData class
#  by just dropping the mapping into the instance namespace dynamically...

Mapping = namedtuple('Mapping',['get_metadata', 'retrieve_raw_data'])

# This defines the actual mappings for each of the ungridded data types
static_mappings = { 'HDF_SD' : Mapping(hdf_sd.get_metadata, hdf_sd.get_data),
                    'HDF_VD' : Mapping(hdf_vd.get_metadata, hdf_vd.get_data),
                    'HDF5'   : '',
                    'netCDF' : Mapping(netcdf.get_metadata, netcdf.get_data) }


class ADelayedData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    def __init__(self, data, metadata, data_type=None):
        '''
        @param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler, but 
                        if no metadata is specified the metadata from the first handler is used
        @param data_type: The type of ungridded data being passed - valid options are the keys in static_mappings
        @param metadata: Any associated metadata
        '''
        from jasmin_cis.exceptions import InvalidDataTypeError
        import numpy as np

        if isinstance(data, np.ndarray):
            # If the data input is a numpy array we can just copy it in and ignore the data_manager
            self._data = data
            self._data_manager = None
            if data_type is not None:
                raise InvalidDataTypeError
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

            if data_type in static_mappings:
                # Set the method names defined in static_mappings to their mapped function names
                for method_name, mapping in static_mappings[data_type]._asdict().iteritems():
                    setattr(self, method_name, mapping)
            else:
                raise InvalidDataTypeError

        self._metadata = metadata
        metadata.copy_attributes_into(self)

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

    def copy_metadata_from(self, other_data):
        '''
            Method to copy the metadata from one UngriddedData/Cube object to another
        '''
        self._coords = other_data.coords()
        self._metadata = other_data._metadata

        #def __getitem__(self, item): pass
        # This method can be overridden to provide the ability to ask for slices of data e.g. UngridedDataObject[012:32.4:5]
        # Actually implementing it would be very tricky as you have to keep track of the data and the coordinates without
        #  necessarily actually reading them


class Coord(ADelayedData):

    def __init__(self, data, metadata, axis, data_type=None):
        super(Coord, self).__init__(data, metadata, data_type)
        self.axis = axis
        self._name = metadata.name

    def name(self):
        return self._name # String


class UngriddedData(ADelayedData):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    @classmethod
    def from_points_array(cls, hyperpoints):
        """
         A constuctor for building an UngriddedData object from a list of hyper points
        Note: This method is unfinished
        @param hyperpoints:    A list of HyperPoints
        """
        from numpy import array
        latitude = []
        longitude = []
        values = []

        for hyperpoint in hyperpoints:
            latitude.append(hyperpoint.latitude)
            longitude.append(hyperpoint.longitude)
            values.append(hyperpoint.val[0])

        return cls(array(values), array(latitude), array(longitude))

    def __init__(self, data, coords, metadata, data_type=None):
        '''
        Constructor

        args:
            data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler, but
                        if no metadata is specified the metadata from the first handler is used
            data_type: The type of ungridded data being passed - valid options are
                        the keys in static_mappings
            metadata: Any associated metadata
        '''
        super(UngriddedData, self).__init__(data, metadata, data_type)

        self._coords = coords

    @property
    def x(self):
        return self.coord(axis='X')

    @property
    def y(self):
        return self.coord(axis='Y')

    def coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a list of coordinates in this UngriddedData object fitting the given criteria. This is deliberately very
         similar to Cube.coords() to maintain a similar interface and because the functionality is similar. There
          is no distrinction between dimension coordinates and auxilliary coordinates here though.

        @param name:  The standard name or long name or default name of the desired coordinate.
            If None, does not check for name. Also see, :attr:`Cube.name`.
        @param standard_name: The CF standard name of the desired coordinate. If None, does not check for standard name.
        @param long_name: An unconstrained description of the coordinate. If None, does not check for long_name.
        @param attributes: A dictionary of attributes desired on the coordinates. If None, does not check for attributes.
        @param axis: The desired coordinate axis, see :func:`iris.util.guess_coord_axis`. If None, does not check for axis.
            Accepts the values 'X', 'Y', 'Z' and 'T' (case-insensitive).

        @return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        from collections import Mapping
        coords = self._coords

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

    def coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a single coord given the same arguments as L(coords). If the arguments given do not result in precisely
         1 coordinate being matched, a CoordinateNotFoundError is raised.

        @raise: CoordinateNotFoundError
        @return: A single coord given the same arguments as L(coords).

        """
        from iris.exceptions import CoordinateNotFoundError
        coords = self.coords(name=name, standard_name=standard_name, long_name=long_name, attributes=attributes, axis=axis)

        if len(coords) > 1:
            msg = 'Expected to find exactly 1 coordinate, but found %s. They were: %s.'\
                  % (len(coords), ', '.join(coord.name() for coord in coords))
            raise CoordinateNotFoundError(msg)
        elif len(coords) == 0:
            bad_name = name or standard_name or long_name or ''
            msg = 'Expected to find exactly 1 %s coordinate, but found none.' % bad_name
            raise CoordinateNotFoundError(msg)

        return coords[0]

