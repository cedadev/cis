'''
module to test the abstract read interface - it's job is to handle the gridded/ungridded switch - and this is all that needs
  to be tested here. There are tests other tests for after the choice has been made between gridded and ungridded.
'''
from nose.tools import istest, eq_, raises
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.read import *
from jasmin_cis.exceptions import FileIOError, CISError
import jasmin_cis.data_io.read as cis_read
from iris.cube import Cube
from jasmin_cis.data_io.ungridded_data import UngriddedData

@istest
def can_read_netcdf_file_when_reading_variables():
    filename = valid_1d_filename
    assert(isinstance(cis_read.read_all_variables_from_file(filename), list))

@istest
def can_read_netcdf_file_when_loading_a_cube():
    filename = valid_1d_filename
    assert(isinstance(cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename), Cube))

@istest
def can_read_gdf_file_when_loading_ungridded_data():
    filename = valid_cloudsat_RVOD_file
    assert(isinstance(cis_read.read_variable_from_files(filename, valid_cloudsat_RVOD_variable), UngriddedData))

@istest
@raises(CISError)
def should_raise_ciserror_with_invalid_filename_when_reading_variables():
    filename = invalid_filename
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(IOError)
def should_raise_ioerror_with_invalid_filename_when_loading_a_cube():
    filename = invalid_filename
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(CISError)
def should_raise_ciserror_with_file_that_is_not_netcdf_when_reading_variables():
    filename = non_netcdf_file
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(ValueError, FileIOError)
def should_raise_valueerror_or_fileioerror_with_file_that_is_not_a_recognised_format_when_loading():
    filename = non_netcdf_file
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
def test_read_file_coordinates():
    #read_file_coordinates(filename)
    pass