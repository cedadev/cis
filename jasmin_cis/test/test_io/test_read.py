'''
Module to test the reading of NetCDF files
More tests for reading can be found in the manual_integration_tests package
'''
from nose.tools import istest, raises
from jasmin_cis.test.test_files.data import *
from jasmin_cis.exceptions import *
import jasmin_cis.data_io.read as cis_read
from pyhdf.error import HDF4Error

@istest
def can_read_netcdf_file_when_reading_variables():
    filename = valid_1d_filename
    cis_read.read_all_variables_from_file(filename)

@istest
def can_read_netcdf_file_when_loading_a_cube():
    filename = valid_1d_filename
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(HDF4Error)
def should_raise_hdf4error_with_invalid_filename_when_reading_variables():   
    filename = invalid_filename
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(IOError)
def should_raise_ioerror_with_invalid_filename_when_loading_a_cube():
    filename = invalid_filename
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(HDF4Error)
def should_raise_hdf4error_with_file_that_is_not_netcdf_when_reading_variables():      
    filename = non_netcdf_file
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(ValueError, FileIOError)
def should_raise_valueerror_or_fileioerror_with_file_that_is_not_a_recognised_format_when_loading():    
    filename = non_netcdf_file    
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(HDF4Error)
def should_raise_hdf4error_with_file_that_does_not_have_read_permissions_when_reading_variables():
    filename = file_without_read_permissions
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(IOError)
def should_raise_ioerror_with_file_that_does_not_have_read_permissions_when_loading_a_cube():    
    filename = file_without_read_permissions
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)        

@istest
def can_read_netcdf_file_with_incorrect_file_extension_when_reading_variables():
    filename = netcdf_file_with_incorrect_file_extension
    cis_read.read_all_variables_from_file(filename)
    
@istest
def can_read_netcdf_file_with_incorrect_file_extension_when_loading_a_cube():
    filename = netcdf_file_with_incorrect_file_extension
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(HDF4Error)
def should_raise_hdf4error_with_file_that_has_netcdf_extension_but_is_not_netcdf_when_reading_variables():
    filename = non_netcdf_file_with_netcdf_file_extension
    cis_read.read_all_variables_from_file(filename)

@istest
@raises(FileIOError)
def should_raise_fileioerror_with_file_that_has_netcdf_extension_but_is_not_netcdf_when_loading_a_cube():
    filename = non_netcdf_file_with_netcdf_file_extension
    cis_read.read_variable_from_files(filename, valid_variable_in_valid_filename)

@istest
@raises(InvalidVariableError)
def should_raise_error_when_variable_does_not_exist_in_file_when_loading_a_cube():
    filename = valid_1d_filename
    variable = invalid_variable    
    cis_read.read_variable_from_files([filename], variable)