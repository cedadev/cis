from nose.tools import istest, raises
from jasmin_cis.info import info
from jasmin_cis.exceptions import CISError
from jasmin_cis.test.test_files.data import *

@istest
def can_read_netcdf_file_when_reading_variables():
    filename = valid_1d_filename
    info(filename)

@istest
@raises(CISError)
def should_raise_ciserror_with_invalid_filename_when_reading_variables():
    filename = invalid_filename
    info(filename)

@istest
@raises(CISError)
def should_raise_ciserror_with_file_that_is_not_netcdf_when_reading_variables():
    filename = non_netcdf_file
    info(filename)


@istest
@raises(CISError)
def should_raise_ciserror_with_file_that_does_not_have_read_permissions_when_reading_variables():
    filename = file_without_read_permissions
    info(filename)


@istest
def can_read_netcdf_file_with_incorrect_file_extension_when_reading_variables():
    filename = netcdf_file_with_incorrect_file_extension
    cis_read.get_file_variables(filename)

@istest
@raises(CISError)
def should_raise_ciserror_with_file_that_has_netcdf_extension_but_is_not_netcdf_when_reading_variables():
    filename = non_netcdf_file_with_netcdf_file_extension
    cis_read.get_file_variables(filename)
