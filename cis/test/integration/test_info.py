import unittest

from cis.info import info
from cis.test.integration_test_data import *
from cis.data_io.products.AProduct import ProductPluginException


class TestInfo(unittest.TestCase):
    
    def test_test_can_get_info_on_a_netcdf_file(self):
        info(valid_1d_filename)
    
    def test_can_get_info_on_a_variable_in_a_netcdf_file(self):
        info(valid_1d_filename, [valid_1d_variable])
    
    def test_should_raise_error_when_file_is_not_netcdf(self):
        with self.assertRaises(ProductPluginException):
            info(non_netcdf_file_with_netcdf_file_extension)
    
    def test_can_get_info_on_a_cloudsat_file(self):
        info(valid_cloudsat_RVOD_file)
    
    def test_can_get_info_on_a_variable_in_a_cloudsat_file(self):
        info(valid_cloudsat_RVOD_file, [valid_cloudsat_RVOD_sdata_variable])
    
    def test_can_get_info_on_a_modis_file(self):
        info(valid_modis_l2_filename)
    
    def test_can_get_info_on_a_variable_in_a_modis_file(self):
        info(valid_modis_l2_filename, [valid_modis_l2_variable])
    
    def test_can_get_info_on_an_aeronet_file(self):
        info(valid_aeronet_filename)
    
    def test_can_get_info_on_a_variable_in_an_aeronet_file(self):
        info(valid_aeronet_filename, [valid_aeronet_variable])
    
    def test_can_get_info_on_a_caliop_file(self):
        info(valid_caliop_l2_filename)
    
    def test_can_get_info_on_a_variable_in_a_caliop_file(self):
        info(valid_caliop_l2_filename, [valid_caliop_l2_variable])
    
    def test_can_get_info_on_a_caliop_l1_file(self):
        info(valid_caliop_l1_filename)
    
    def test_can_get_info_on_a_variable_in_a_caliop_l1_file(self):
        info(valid_caliop_l1_filename, [valid_caliop_l1_variable])
