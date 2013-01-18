'''
Class for ungridded data and utilities for handling it
'''

def read_ungridded_data(filenames, variables):
    '''
    Read ungridded data from a file
    Note: Not yet implemented
    
    args:
        filenames:    List of filenames of files to read
        variables:    List of variables to read from the files
    '''
    from jasmin_cis.exceptions import CISError
    raise CISError

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
        
        