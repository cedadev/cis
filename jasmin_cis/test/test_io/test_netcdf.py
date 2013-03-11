'''
module to test the NetCDF module
'''
from netCDF4 import Variable
from nose.tools import istest,raises, eq_
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.netcdf import *

@istest
@raises(IOError)
def should_raise_io_error_with_file_that_is_not_netcdf():
    read(valid_aeronet_filename, valid_aeronet_variable)

@istest
def test_that_can_read_all_variables():
    dict = get_netcdf_file_variables(valid_2d_filename)
    eq_(len(dict),426)

@istest
def test_that_can_read_known_variable():
    data = read(valid_2d_filename,'latitude')
    assert(isinstance(data['latitude'],Variable))

@istest
def test_that_can_get_data():
    data = read(valid_2d_filename, 'latitude')
    eq_(data['latitude'].shape,(145,))

@istest
def test_that_can_get_metadata_for_known_variable():
    data = read(valid_2d_filename,'rain')
    metadata = get_metadata(data['rain'])

    eq_(str(metadata.missing_value),"2e+20")
    eq_(metadata.long_name,"TOTAL RAINFALL RATE: LS+CONV KG/M2/S")
    eq_(metadata.units,"kg m-2 s-1")

@istest
@raises(IOError)
def should_raise_ioerror_with_file_that_does_not_have_read_permissions():
    read(file_without_read_permissions, valid_variable_in_valid_filename)

