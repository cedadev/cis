'''
    Module for the UngriddedData class
'''
from collections import namedtuple
import hdf_vd as hdf_vd
import hdf_sd as hdf_sd

# Define the vars of the methods that must be mapped to, these are the methods UngriddedData objects will call
#  I think this could actually define the EXTERNAL interface without creating any sub methods in the UngriddedData class
#  by just dropping the mapping into the instance namespace dynamically...

Mapping = namedtuple('Mapping',['get_metadata', 'retrieve_raw_data'])

# This defines the actual mappings for each of the ungridded data types
static_mappings = { 'HDF_SD' : Mapping(hdf_sd.get_metadata, hdf_sd.get_data),
                    'HDF_VD' : Mapping(hdf_vd.get_metadata, hdf_vd.get_data),
                    'HDF5'   : '',
                    'netCDF' : '' }

class UngriddedData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''

    @classmethod
    def from_points_array(cls, hyperpoints):
        """
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

    class Coord(object):
        def __init__(self, name):
            self._name = name
        def name(self):
            return self._name # String

    def __init__(self, data, lat=None, lon=None, height=None, time=None, data_type=None, metadata=None):
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
        from jasmin_cis.exceptions import InvalidDataTypeError
        import numpy as np

        if isinstance(data, np.ndarray):
            self._data = data
            self._data_manager = None
            if data_type is not None:
                raise InvalidDataTypeError
        else:
            self._data = None
            # Although the data can be a list or a single item it's useful to cast it
            #  to a list here to make accessing it consistent
            if isinstance(data, list):
                self._data_manager = data
            else:
                self._data_manager = [ data ]

            if data_type in static_mappings:
                # Store the mappings in a private variable for use in getarr
                self._map = static_mappings[data_type]._asdict()
            else:
                raise InvalidDataTypeError

        if metadata is None:
            if self._data_manager is not None:
                # Retrieve metadata for the first variabel - assume this is the variable of interest
                self._metadata = self.get_metadata(self._data_manager[0])
            else:
                self._metadata = None
        else:
            self._metadata = metadata

        # Copy in the various coordinate arrays
        self.lat = lat
        self.lon = lon
        self.alt = height
        # Turn the time vector into an array for use with pcolormesh - may be easier to copy
        if time is not None:
            self.time = np.meshgrid(np.arange(0,len(height[1])), time)[1]
        else:
            self.time = None

        # coords is a list of coord objects
        coords = [ UngriddedData.Coord('Time'), UngriddedData.Coord('Height')]
        self._coords = coords

        if self._metadata is not None:
            # Metadata should really be stored as a seperate object in an UngriddedData instance - even if it's just a namedtuple
            # NOTE - it would be good to use .get on info and attributes to be able to set defaults
            self.name = self._metadata["info"][0]
            if isinstance(self._metadata["info"][2], list):
                self.shape = self._metadata["info"][2]
            else:
                self.shape = [ self._metadata["info"][2] ]
            self.long_name = self._metadata["attributes"]["long_name"]
            self.units = self._metadata["attributes"]["units"]
            self.missing_value = self._metadata["attributes"].get('_FillValue', None)

            #self.range = self.metadata["attributes"]["range"]
            #self.type = v_type
            #self.short_name = short_name
            #self.data_list = [x, y, data]


    @property
    def x(self):
        if self.time is not None:
            return self.time
        else:
            return self.lat

    @property
    def y(self):
        if self.alt is not None:
            return self.alt
        else:
            return self.lon

    def coords(self, contains_dimension = None, dim_coords = None):
        return self._coords # list of object Coord

    #    def _find_metadata(self):
    #        self.metadata = self.map.get_metadata(self._data)

    def __getattr__(self,attr):
        '''
            This little method actually provides the mapping between the method calls.
            It overrides the default getattr method which is only called if no attributes of name 'attr'
            can be found, hence if we don't deal with it we need to raise an AttributeError.
        '''
        if attr in self._map:
            return self._map[attr]
        else:
            # Default behavior
            raise AttributeError

    @property
    def data(self):
        '''
            This is a getter for the data property. It caches the raw data if it has not already been read.
             Throws a MemoryError when reading for the first time if the data is too large.
        '''
        import numpy as np
        if self._data is None:
            try:
                # If we ere given a list of data managers then we need to concatenate them now...
                self._data=self.retrieve_raw_data(self._data_manager[0])
                if len(self._data_manager) > 1:
                    for manager in self._data_manager[1:]:
                        self._data = np.concatenate((self._data,self.retrieve_raw_data(manager)),axis=0)
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
        self.standard_name = other_data.standard_name
        self.shape = other_data.shape
        self.long_name = other_data.long_name
        self.units = other_data.units

    