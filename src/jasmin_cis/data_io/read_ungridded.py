# Created by PARD on 14th Jan 2013
# Copyright TODO
#
# Class for ungridded data and utilities for handling it

def read_ungridded_data(filenames, variables):
    from jasmin_cis.exceptions import CISError
    raise CISError

class UngriddedData():
    def __init__(self, data=None):
        self._data = data
        # numpy array for the actual data? Maybe see sat.hdf.py
        
        