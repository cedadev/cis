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

@istest
def can_get_info_on_a_cloudsat_file():
    info(valid_cloudsat_RVOD_file)

@istest
def can_get_info_on_a_variable_in_a_cloudsat_file():
    info(valid_cloudsat_RVOD_file, [valid_cloudsat_RVOD_sdata_variable])

@istest
def can_get_info_on_a_modis_file():
    info(valid_modis_l2_filename)

@istest
def can_get_info_on_a_variable_in_a_modis_file():
    info(valid_modis_l2_filename, [valid_modis_l2_variable])

@istest
def can_get_info_on_an_aeronet_file():
    info(valid_aeronet_filename)

@istest
def can_get_info_on_a_variable_in_an_aeronet_file():
    info(valid_aeronet_filename, [valid_aeronet_variable])

@istest
def can_get_info_on_a_caliop_file():
    info(valid_caliop_l2_filename)

@istest
def can_get_info_on_a_variable_in_a_caliop_file():
    info(valid_caliop_l2_filename, [valid_caliop_l2_variable])

@istest
def can_get_info_on_a_caliop_l1_file():
    info(valid_caliop_l1_filename)

@istest
def can_get_info_on_a_variable_in_a_caliop_l1_file():
    info(valid_caliop_l1_filename, [valid_caliop_l1_variable])