from netCDF4 import Dataset
import os
import unittest
from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to


class BaseIntegrationTest(unittest.TestCase):

    OUTPUT_NAME = 'test_integration_out'
    UNGRIDDED_OUTPUT_FILENAME = 'cis-' + OUTPUT_NAME + ".nc"
    GRIDDED_OUTPUT_FILENAME = OUTPUT_NAME + ".nc"

    def setUp(self):
        self.clean_output()

    def tearDown(self):
        return
        self.clean_output()

    def clean_output(self):
        for path in self.UNGRIDDED_OUTPUT_FILENAME, self.GRIDDED_OUTPUT_FILENAME:
            if os.path.exists(path):
                os.remove(path)

    def check_output_contains_variables(self, output_path, var_names):
        ds = Dataset(output_path)
        for var in var_names:
            try:
                var = ds.variables[var]
            except KeyError:
                raise AssertionError("Variable %s not found in subset output file" % var)

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