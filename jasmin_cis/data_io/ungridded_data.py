'''
    Module for the UngriddedData class
'''
from netCDF4 import _Variable, Variable
from netcdf import get_data as netcdf_get_data
from hdf_vd import get_data as hdf_vd_get_data, VDS
from pyhdf.SD import SDS
from hdf_sd import get_data as hdf_sd_get_data


class Metadata(object):

    @classmethod
    def from_CubeMetadata(cls, cube_meta):
        return cls(name='',standard_name=cube_meta.standard_name,long_name=cube_meta.long_name, units=str(cube_meta.units), misc=cube_meta.attributes)

    def __init__(self, name='', standard_name='', long_name='', shape='', units='', range='', factor='', offset='', missing_value='', misc=None):
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
        if misc is None:
            self.misc = {}
        else:
            self.misc = misc

    @staticmethod
    def guess_standard_name(name):
        standard_name = ''
        if name.lower().startswith('lat'):
            standard_name = 'latitude'
        elif name.lower().startswith('lon'):
            standard_name = 'longitude'
        elif name.lower().startswith('alt') or name.lower() == 'height':
            standard_name = 'altitude'
        return standard_name


# This defines the mappings for each of the ungridded data types to their reading routines, this allows 'lazy loading'
static_mappings = { SDS : hdf_sd_get_data,
                    VDS : hdf_vd_get_data,
                    Variable : netcdf_get_data,
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
        from iris.cube import CubeMetadata
        import numpy as np
        from utils import copy_attributes

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
                # Set the retrieve_raw_data method to it's mapped function name
                self.retrieve_raw_data = static_mappings[self._data_manager[0].__class__]
            else:
                raise InvalidDataTypeError

        if isinstance(metadata, CubeMetadata):
            self._metadata = Metadata.from_CubeMetadata(metadata)
        else:
            self._metadata = metadata
        copy_attributes(self._metadata, self)

    def name(self):
        """
            This routine returns the first name property which is not empty out of: _name, standard_name and long_name
                If they are all empty it returns an empty string
        @return: The name of the data object as a string
        """
        for name in [self._name, self.standard_name, self.long_name]:
            if name:
                return name
        return ''

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
        from data_io.Coord import CoordList, Coord

        super(UngriddedData, self).__init__(data, metadata)

        if isinstance(coords, list):
            self._coords = CoordList(coords)
        elif isinstance(coords, CoordList):
            self._coords = coords
        elif isinstance(coords, Coord):
            self._coords = CoordList([coords])
        else:
            raise ValueError("Invalid Coords type")
    
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


    def coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """

        @return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        return self._coords.get_coords(name, standard_name, long_name, attributes, axis)

    def coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """

        @raise: CoordinateNotFoundError
        @return: A single coord given the same arguments as L(coords).

        """
        return self._coords.get_coord(name, standard_name, long_name, attributes, axis)

    def get_points(self):
        """
             Pack a list of coordinates into a list of x, y, z, t points
        @param coords: A CoordList of Coord objects
        @return: A list of HyperPoints
        """
        import numpy as np
        from hyperpoint import HyperPoint
        points = []

        lat = self.coord(standard_name='latitude').data.flatten()
        lon = self.coord(standard_name='longitude').data.flatten()
        alt = self.coord(standard_name='altitude').data.flatten()
        time = self.coord(standard_name='time').data.flatten()
        data = self.data.flatten()

        for x ,lat_p in np.ndenumerate(lat):
            points.append(HyperPoint(lat_p,lon[x],alt[x],time[x],data[x]))

        return points
