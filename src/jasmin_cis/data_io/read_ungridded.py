'''
Class for ungridded data and utilities for handling it
'''
from pyhdf.error import HDF4Error
import hdf
import numpy as np
from glob import glob

def read_ungridded_data(filenames, variables, vdata=False):
    '''
    Read ungridded data from a file
    Note: Not yet implemented
    
    args:
        filenames:    List of filenames of files to read
        variables:    List of variables to read from the files
        vdata:        Is the data stored as VD (as opposed to SD)
    '''
    from jasmin_cis.exceptions import FileIOError
    
    outdata = {}
    for filename in filenames:
        try:
            data = hdf.read_hdf4(filename,variables,vdata)
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


class UngriddedData():
    '''
    Note:Not yet implemented
    '''
    def __init__(self, data=None):
        '''
        Constructor
        
        args:
            data:    Optional
        '''
        self._data = data
        # numpy array for the actual data? Maybe see sat.hdf.py
        
        