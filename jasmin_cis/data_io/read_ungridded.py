'''
Class for ungridded data and utilities for handling it
'''
from pyhdf.error import HDF4Error
import hdf
import numpy as np
from glob import glob
from collections import namedtuple
from hdf import get_hdf4_SD_data, get_hdf4_VD_data, read_hdf4_SD_metadata, get_hdf_VD_file_variables

def read_ungridded_data_coordinates(filename):
    '''
        Read in coordinate variables and pass back arrays for lat, lon and vals
    '''
    pass

def get_netcdf_file_coordinates_points(filename):
    '''
        Convert coordinate arrays into a list of points for colocation sampling
        
    '''
    from jasmin_cis.col import HyperPoint
    
    lat, lon, vals = read_ungridded_data_coordinates(filename)
    
    # Pack the data into a list of x,y, val points to be passed to col
    points = []    
    
    for (x,y), value in np.ndenumerate(vals):
        lat = lat[x,y]
        lon = lon[x,y]
        points.append(HyperPoint(lat,lon, val=value))
        
    return points

def read_ungridded_data(filenames, variables):
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

def read_satelite_data(folder,day,year,variable,orbits=None): 
    '''
    Reads in data from General satelie Level2 data files. 
    Also reads in some geolocation data (lat,lon,TAI time) into the output dictionary. 
    Setting outdata allows the data to be read into an already exisiting dictionary.
    '''   
    day = str(day).rjust(3,'0')
    
    if orbits is None:
        filenames = glob(folder + str(year) + '/' + str(day) + '/*')
        filenames = np.sort(filenames)
    else:
        filenames = []
        for orbit in orbits:
            filenames.append(glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')[0])
    names = variable+['Latitude','Longitude','TAI_start','Profile_time']
    
    return read_ungridded_data(filenames, names)


# Define the names of the methods that must be mapped to, these are the methods UngriddedData objects will call
#  I think this could actually define the EXTERNAL interface without creating any sub methods in the UngriddedData class
#  by just dropping the mapping into the instance namespace dynamically...
Mapping = namedtuple('Mapping',['get_metadata', 'retrieve_raw_data'])

# This defines the actual mappings for each of the ungridded data types
static_mappings = { 'HDF_SD' : Mapping(read_hdf4_SD_metadata, get_hdf4_SD_data),
             'HDF_VD' : Mapping(get_hdf_VD_file_variables, get_hdf4_VD_data),
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
                This si quicker than calling load_ungridded_data as we read multiple variables per file read
        args:
            filenames:    List of filenames of files to read
            variables:    List of variables to read from the files
        '''
        from jasmin_cis.exceptions import FileIOError
        
        outdata = {}
        for filename in filenames:
            try:
                data = hdf.read_hdf4_SD(filename,variables)
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
                data.append(hdf.read_hdf4_SD_variable(filename, variable))
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
    
    