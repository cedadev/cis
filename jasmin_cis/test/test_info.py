from nose.tools import istest, raises
from jasmin_cis.info import info
from jasmin_cis.test.test_files.data import *
from jasmin_cis.exceptions import CISError

@istest
def can_get_info_on_a_netcdf_file():
    info(valid_1d_filename)

@istest
def can_get_info_on_a_variable_in_a_netcdf_file():
    info(valid_1d_filename, [valid_variable_in_valid_filename])

@istest
@raises(CISError)
def should_raise_error_when_file_is_not_netcdf():
    info(non_netcdf_file_with_netcdf_file_extension)