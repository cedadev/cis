from netCDF4 import Dataset
from unittest import TestCase
from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to

from cis import subset_cmd
from parse import parse_args
from test.integration.test_files.data import *


class TestSubsetIntegration(TestCase):

    OUTPUT_FILENAME = 'test_subset_out'
    UNGRIDDED_OUTPUT_FILENAME = 'cis-' + OUTPUT_FILENAME + ".nc"
    GRIDDED_OUTPUT_FILENAME = OUTPUT_FILENAME + ".nc"

    def setUp(self):
        self.clean_output()

    def tearDown(self):
        self.clean_output()

    def clean_output(self):
        for path in self.UNGRIDDED_OUTPUT_FILENAME, self.GRIDDED_OUTPUT_FILENAME:
            if os.path.exists(path):
                os.remove(path)

    def test_GIVEN_single_variable_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_in_gridded_file_WHEN_subset_THEN_subsetted(self):
        variable = valid_hadgem_variable
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_multiple_variables_in_ungridded_file_WHEN_subset_THEN_subsetted(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable1, variable2])

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