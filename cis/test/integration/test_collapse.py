from netCDF4 import Dataset

from cis.cis_main import collapse_cmd
from cis.test.integration.base_integration_test import BaseIntegrationTest
from cis.test.integration_test_data import *
from cis.test.utils_for_testing import *
from cis.parse import parse_args


class TestCollapse(BaseIntegrationTest):
    """
    This class provides integration testing for the Collapse command
    """

    def check_shape_collapse(self, var, expected_shape):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        self.var = self.ds.variables[var]
        assert_that(self.var.shape == expected_shape)
        self.ds.close()

    def test_collapse_over_latlon(self):
        # Takes 20s
        variable = '*'
        filename = valid_hadgem_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean', 'x,y', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['od550aer'])
        self.check_shape_collapse('od550aer', (240,))

    def test_collapse_over_time(self):
        # Takes 14s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean', 't', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))
        self.check_shape_collapse('od550aer', (1, 192, 76))

    @skip_pyhdf
    def test_collapse_MODIS_L3(self):
        # Takes 15s
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean', 'x,y',
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_collapse_cis_gridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_gridded_output_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean,product=NetCDF_Gridded', 'x,y',
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['TAU_2D_550nm'])

    def test_netCDF_gridded_hybrid_height(self):
        # Takes 2s
        variable = valid_hybrid_height_variable
        filename = valid_hybrid_height_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean', 't,x,y', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_netCDF_gridded_hybrid_height_partial(self):
        # JASCIS-126
        # Takes 2s
        variable = valid_hybrid_height_variable
        filename = valid_hybrid_height_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=mean', 't', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_netCDF_gridded_hybrid_height_partial_with_multi_kernel(self):
        # Takes 2s
        variable = valid_hybrid_height_variable
        filename = valid_hybrid_height_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename), 't', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_collapse_MODIS_L3(self):
        # Takes 30s
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        arguments = ['collapse', variable + ':' + escape_colons(filename), 't', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_collapse_netCDF_gridded_HadGem_multikernel(self):
        # Takes 1s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        grid = 'x,y'
        arguments = ['collapse', variable + ':' + escape_colons(filename) + ':kernel=moments', grid, '-o',
                     self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        collapse_cmd(main_arguments)
        expected_vars = ['od550aer', 'od550aer_std_dev', 'od550aer_num_points']
        self.check_output_contains_variables(self.OUTPUT_FILENAME, expected_vars)
