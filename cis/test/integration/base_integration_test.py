from netCDF4 import Dataset
import os
import unittest
from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to, is_


class BaseIntegrationTest(unittest.TestCase):

    OUTPUT_NAME = 'test_integration_out'
    UNGRIDDED_OUTPUT_FILENAME = 'cis-' + OUTPUT_NAME + ".nc"
    GRIDDED_OUTPUT_FILENAME = OUTPUT_NAME + ".nc"

    def setUp(self):
        self.clean_output()

    def tearDown(self):
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
                raise AssertionError("Variable %s not found in output file" % var)

    def check_output_file_variable_attribute_contains_string(self, output_path, variable, attribute, string):
        ds = Dataset(output_path)
        try:
            var = ds.variables[variable]
        except KeyError:
            raise AssertionError("Variable %s not found in output file" % variable)
        try:
            att_string = getattr(var, attribute)
        except AttributeError:
            raise AssertionError("Attribute %s not found in variable" % attribute)
        assert string in att_string

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

    def check_output_col_grid(self, sample_file, sample_var, output_file, output_vars, expected_shape=None):
        """
        Check that the output grid matches the sample grid in shape.
        :param sample_file:
        :param sample_var:
        :param output_file:
        :param output_vars:
        :return:
        """
        from cis import read_data, read_data_list
        from operator import mul
        if expected_shape is None:
            sample_shape = read_data(sample_file, sample_var).data.shape
        else:
            sample_shape = expected_shape
        output = read_data_list(output_file, output_vars)
        for output_var in output:
            output_shape = output_var.data.shape
            # This copes with dims in different orders, length 1 values being taken out etc
            assert_that(reduce(mul, sample_shape), is_(reduce(mul, output_shape)))
