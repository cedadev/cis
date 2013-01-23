'''
Class for ungridded data and utilities for handling it
'''
from pyhdf.error import HDF4Error
import hdf
import numpy as np
from glob import glob
from collections import namedtuple
from hdf import get_hdf4_SD_data, get_hdf4_VD_data, get_hdf_SD_file_variables, get_hdf_VD_file_variables

def read_ungridded_data(filenames, variables):
    '''
    Read ungridded data from a file
    
    args:
        filenames:    List of filenames of files to read
        variables:    List of variables to read from the files
    '''
    from jasmin_cis.exceptions import FileIOError
    
    outdata = {}
    for filename in filenames:
        try:
            data = hdf.read_hdf4_SD(filename,variables)
            data['Profile_time'] = data['Profile_time'] + data['TAI_start']
            for name in data.keys():
                try:
                    outdata[name] = np.hstack((outdata[name],data[name]))
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata[name] = data[name]
        except HDF4Error as e:
            raise FileIOError(str(e)+' for file: '+filename)
    return outdata

def read_satelite_data(folder,day,year,sds,orbits=None,vdata=False): 
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
    names = sds+['Latitude','Longitude','TAI_start','Profile_time']
    
    return read_ungridded_data(filenames, names, vdata)


# Define the names of the methods that must be mapped to, these are the methods UngriddedData objects will call
#  I think this could actually define the EXTERNAL interface without creating any sub methods in the UngriddedData class
#  by just dropping the mapping into the instance namespace dynamically...
Mapping = namedtuple('Mapping',['get_metadata', 'get_data'])

# This defines the actual mappings for each of the ungridded data types
static_mappings = { 'HDF_SD' : Mapping(get_hdf_SD_file_variables,get_hdf4_SD_data),
             'HDF_VD' : Mapping(get_hdf_VD_file_variables,get_hdf4_VD_data),
             'HDF5'   : '',
             'netCDF' : '' }

class UngriddedData(object):
    '''
        Wrapper (adaptor) class for the different types of possible ungridded data.
    '''
    
    @classmethod
    def load(filenames, variables):
        '''
            Return a list of UngriddedData objects
        '''
        pass
    
    @classmethod
    def load_ungridded_data(filenames, variable):
        '''
            Return an UngriddedData object
        '''
        pass
    
    
    def __init__(self, data_ref, data_type, metadata=None):
        '''
        Constructor
        
        args:
            data:    The data handler for the specific data type - NOT the data itself
            data_type: The type of ungridded data being passed - valid options are
                        the keys in 
            metadata: Any associated metadata
        '''
        from jasmin_cis.exceptions import InvalidDataTypeError
        
        self._data = data_ref
        
        if data_type in static_mappings:
            self.data_type = data_type
            #self.map = static_mappings[data_type]
            # Perform the function mapping
            for func, map in static_mappings[data_type]._asdict().items():
                self.func = map
        else:
            raise InvalidDataTypeError
        
        if metadata is None:
            self.metadata = self.get_metadata(self._data)
        else:
            self.metadata = metadata
        
#    def _find_metadata(self):
#        self.metadata = self.map.get_metadata(self._data)    
    
    @property
    def data(self):
        pass