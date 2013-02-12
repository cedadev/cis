'''
    Module for the UngriddedData class
'''
from netCDF4 import _Variable
from netcdf import get_data as netcdf_get_data
from hdf_vd import get_data as hdf_vd_get_data, VS_Container
from pyhdf.SD import SD
from hdf_sd import get_data as hdf_sd_get_data


class Metadata(object):

    def __init__(self, name='', long_name='', shape='', units='', range='', factor='', offset='', missing_value='', misc=None):
        self._name = name
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


# This defines the mappings for each of the ungridded data types to their reading routines, this allows 'lazy loading'
static_mappings = { SD : hdf_sd_get_data,
                    VS_Container : hdf_vd_get_data,
                    _Variable : netcdf_get_data }

class LazyData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    def __init__(self, data, metadata):
        '''
        @param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler
        @param metadata: Any associated metadata
        '''
        from jasmin_cis.exceptions import InvalidDataTypeError
        import numpy as np

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

            # Check that we recognise the data manager and that they are all the same
            if self._data_manager[0].__class__ in static_mappings and all([d.__class__ == self._data_manager[0].__class__ for d in self._data_manager ]) :
                # Set the method names defined in static_mappings to their mapped function names
                setattr(self, "retrieve_raw_data", static_mappings[self._data_manager[0].__class__])
            else:
                raise InvalidDataTypeError

        self._metadata = metadata
        metadata.copy_attributes_into(self)

    def name(self):
        return self._name # String

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


class Coord(LazyData):

    def __init__(self, data, metadata, axis=''):
        """

        @param data:
        @param metadata:
        @param axis: A string label for the axis, e.g. 'X', 'Y', 'Z', or 'T'
        @return:
        """
        super(Coord, self).__init__(data, metadata)
        self.axis = axis.upper()

class UngriddedData(LazyData):
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

    def __init__(self, data, metadata, coords):
        '''
        Constructor

        @param data:    The data handler (e.g. SDS instance) for the specific data type, or a numpy array of data
                        This can be a list of data handlers, or a single data handler
        @param coords: A list of the associated Coord objects
        @param metadata: Any associated metadata
        '''
        super(UngriddedData, self).__init__(data, metadata)

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

