from netCDF4 import Dataset

from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to

from jasmin_cis.cis import subset_cmd
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest


class TestSubsetIntegration(BaseIntegrationTest):

    def test_GIVEN_single_variable_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_hadgem_variable
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_multiple_variables_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_multiple_variables_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_echamham_variable_1
        variable2 = valid_echamham_variable_2
        filename = valid_echamham_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_multiple_gridded_variables_on_different_grids_WHEN_subset_THEN_subset_correctly(self):
        variable1 = 'v_1'
        variable2 = 'rh'
        filename = valid_1d_filename
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'y=[%s,%s]' % (lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        lat = ds.variables['latitude'][:]
        assert_that(min(lat), greater_than_or_equal_to(lat_min))
        assert_that(max(lat), less_than_or_equal_to(lat_max))
        lat_1 = ds.variables['latitude_1'][:]
        assert_that(min(lat_1), greater_than_or_equal_to(lat_min))
        assert_that(max(lat_1), less_than_or_equal_to(lat_max))
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_variables_specified_by_wildcard_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = 'surface_albedo???'
        variable2 = 'AOD*'
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, ['AOD550', 'AOD870', 'surface_albedo550',
                                                                              'surface_albedo670', 'surface_albedo870'])


class TestSubsetIntegrationAllProductsAllValidVariables(BaseIntegrationTest):

    def do_subset(self, filename, lat_max, lat_min, lon_max, lon_min, variable):
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def test_subset_netCDF_gridded_xenida(self):
        variable = '*'  # valid_xenida_variable
        filename = valid_xenida_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_netCDF_gridded_xglnwa(self):
        variable = '*'  # valid_1d_variable
        filename = valid_1d_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_netCDF_gridded_ECHAMHAM(self):
        variable = '*'  # valid_echamham_variable
        filename = valid_echamham_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_NCAR_RAF(self):
        variable = '*'  # valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_cis_ungridded(self):
        variable = '*'  # 'AOT_440'
        filename = valid_cis_col_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_cis_gridded(self):
        variable = '*'  # 'AOT_440'
        filename = valid_cis_gridded_output_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_Aerosol_CCI(self):
        variable = '*'  # valid_aerosol_cci_filename
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_Cloud_CCI(self):
        variable = '*'  # valid_aerosol_cci_filename
        filename = valid_cloud_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_Caliop_L2(self):
        variable = '*'  # valid_caliop_l2_variable
        filename = valid_caliop_l1_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_MODIS_L2(self):
        variable = '*'  # valid_modis_l2_variable
        filename = valid_modis_l2_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_MODIS_L3(self):
        variable = '*'  # valid_modis_l3_variable
        filename = valid_modis_l3_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)

    def test_subset_Aeronet(self):
        variable = '*'  # valid_aeronet_variable
        filename = valid_aeronet_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_ASCII(self):
        variable = '*'  # valid_ascii_variable
        filename = valid_ascii_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_CloudSatRVOD(self):
        variable = '*'  # valid_cloudsat_RVOD_sdata_variable
        filename = valid_cloudsat_RVOD_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_CloudSatPRECIP(self):
        variable = '*'  # valid_cloudsat_PRECIP_variable
        filename = valid_cloudsat_PRECIP_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)