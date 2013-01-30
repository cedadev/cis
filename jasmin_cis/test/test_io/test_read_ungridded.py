'''
module to test the reading of ungridded data files
'''
from nose.tools import istest, eq_
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.read_ungridded import get_file_coordinates

@istest
def can_get_coordinates_from_file():
    filename = valid_hdf_sd_file
    data = get_file_coordinates(filename)
    
    eq_(data[0].shape,data[1].shape)
    eq_(data[0].shape,(203,135))
    eq_(data[1].shape,(203,135))

