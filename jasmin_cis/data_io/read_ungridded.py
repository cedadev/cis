'''
Module for reading ungridded data in HDF4 format
'''
import numpy as np
from collections import namedtuple
import hdf_vd as hdf_vd
import hdf_sd as hdf_sd
from pyhdf.error import HDF4Error

def get_file_variables(filename):
    '''
    Get all variables from a file containing ungridded data.
    Concatenate variable from both VD and SD data
    
    args:
        filename: The filename of the file to get the variables from
    
    '''
    SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)
    VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)
    
    return SD_vars, VD_vars


def get_file_coordinates(filename):
    '''
    Read in coordinate variables and pass back tuple of lat, lon,
    each element of tuple being a 2D numpy array
    '''

    data = hdf_vd.get_hdf4_VD_data(filename,['Latitude','Longitude'])
    lat = data['Latitude'].get()
    long = data['Longitude'].get()
    
    return (lat,long)


def get_file_coordinates_points(filename):
    '''
    Convert coordinate arrays into a list of points
    useful or colocation sampling   
    '''
    from jasmin_cis.hyperpoint import HyperPoint
    
    latitude, longitude = get_file_coordinates(filename)
    
    points = []    
    
    for (x,y), lat in np.ndenumerate(latitude):
        lon = longitude[x,y]
        points.append(HyperPoint(lat,lon))
        
    return points


def read(filenames, variables):
    '''
    Read ungridded data from a file. Just a wrapper that calls the appropriate class method based on
        whether in the inputs are lists or not
    
    args:
        filenames:    List of filenames of files to read
        variables:    List of variables to read from the files
    '''
    if isinstance(filenames,list):
        if isinstance(variables, list):
            return UngriddedData.load_ungridded_data_list(filenames, variables)
        else:
            return UngriddedData.load_ungridded_data(filenames, variables)
    else:
        if isinstance(variables, list):
            return UngriddedData.load_ungridded_data_list([filenames], variables)
        else:
            return UngriddedData.load_ungridded_data([filenames], variables)             


# Define the vars of the methods that must be mapped to, these are the methods UngriddedData objects will call
#  I think this could actually define the EXTERNAL interface without creating any sub methods in the UngriddedData class
#  by just dropping the mapping into the instance namespace dynamically...

Mapping = namedtuple('Mapping',['get_metadata', 'retrieve_raw_data'])

# This defines the actual mappings for each of the ungridded data types
static_mappings = { 'HDF_SD' : Mapping(hdf_sd.read_hdf4_SD_metadata, hdf_sd.get_hdf4_SD_data),
             'HDF_VD' : Mapping(hdf_vd.get_hdf_VD_file_variables, hdf_vd.get_hdf4_VD_data),
             'HDF5'   : '',
             'netCDF' : '' }

class UngriddedData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''
    
    @classmethod
    def load_ungridded_data_list(cls, filenames, variables):
        '''
            Return a dictionary of UngriddedData objects, one for each variable - the key is the variable name
                This is quicker than calling load_ungridded_data as we read multiple variables per file read
        args:
            filenames:    List of filenames of files to read
            variables:    List of variables to read from the files
        '''
        from jasmin_cis.exceptions import FileIOError
        
        outdata = {}
        for filename in filenames:
            try:
                data = hdf_sd.read_hdf4_SD(filename,variables)
                for name in data.keys():
                    try:
                        outdata[name].append(data[name])
                    except KeyError:
                        #print KeyError, ' in readin_cloudsat_precip'
                        outdata[name] = data[name]
            except HDF4Error as e:
                raise FileIOError(str(e)+' for file: '+filename)
        for variable in outdata.keys():
            outdata[variable] = cls(outdata[variable],'HDF_SD')
        return outdata
    
    @classmethod
    def load_ungridded_data(cls, filenames, variable):
        '''
            Return an UngriddedData object, for the specified input variable
        
        args:
            filenames:    List of filenames of files to read
            variable:    Variable to read from the files
        '''
        from jasmin_cis.exceptions import FileIOError
        
        data = []
        for filename in filenames:
            try:
                data.append(hdf_sd.read_hdf4_SD_variable(filename, variable))
            except HDF4Error as e:
                raise FileIOError(str(e)+' for file: '+filename)
        return cls(data,'HDF_SD')
    

    def __init__(self, data, data_type=None, metadata=None):
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
                self.metadata = self.get_metadata(self._data_manager[0])
            else:
                self.metadata = None
        else:
            self.metadata = metadata
        
#    def _find_metadata(self):
#        self.metadata = self.map.get_metadata(self._data)    
    
    def __getattr__(self,attr):
        '''
            This little method actually provides the mapping between the method calls.
            It overrides the default getattr method.
        '''
        return self._map[attr]
    
    @property
    def data(self):
        '''
            This is a getter for the data property. It caches the raw data if it has not already been read.
             Throws a MemoryError when reading for the first time if the data is too large.
        '''
        if self._data is None:
            try:
                # If we ere given a list of data managers then we need to concatenate them now...
                self._data=self.retrieve_raw_data(self._data_manager[0])
                if len(self._data_manager) > 1:
                    for manager in self._data_manager[1:]:
                        self._data = np.hstack(self._data,self.retrieve_raw_data(manager))
            except MemoryError:
                raise MemoryError(
                  "Failed to read the ungridded data as there was not enough memory available.\n" 
                  "Consider freeing up variables or indexing the cube before getting its data.")
        return self._data
    
    