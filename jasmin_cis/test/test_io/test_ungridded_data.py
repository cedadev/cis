'''
module to test the reading of ungridded data files
'''
from nose.tools import istest, eq_, raises, nottest
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.read_ungridded import *
from pyhdf.error import HDF4Error
from jasmin_cis.exceptions import InvalidVariableError

@nottest
def from_points_array_returns_valid_ungridded_data_object():
    pass

@nottest
def can_create_ungridded_data_object_from_numpy_array():
    pass

@nottest
def can_create_ungridded_data_object_from_hdf_vd_obj():
    pass

@nottest
def can_create_ungridded_data_object_from_hdf_sd_obj():
    pass

@nottest
def can_create_ungridded_data_object_from_netcdf_data_obj():
    pass