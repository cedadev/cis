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

    def check_latlon_subsetting(self, lat_max, lat_min, lon_max, lon_min, gridded):
        if gridded:
            lat_name = 'lat'
            lon_name = 'lon'
            output_path = self.GRIDDED_OUTPUT_FILENAME
        else:
            lat_name = 'latitude'
            lon_name = 'longitude'
            output_path = self.UNGRIDDED_OUTPUT_FILENAME
        ds = Dataset(output_path)
        lat = ds.variables[lat_name][:]
        lon = ds.variables[lon_name][:]
        assert_that(min(lon), greater_than_or_equal_to(lon_min))
        assert_that(max(lon), less_than_or_equal_to(lon_max))
        assert_that(min(lat), greater_than_or_equal_to(lat_min))
        assert_that(max(lat), less_than_or_equal_to(lat_max))

    def check_output_contains_variables(self, output_path, var_names):
        ds = Dataset(output_path)
        for var in var_names:
            try:
                var = ds.variables[var]
            except IndexError:
                raise AssertionError("Variable %s not found in subset output file" % var)