from netCDF4 import Dataset
import os
import unittest
from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to, is_
from functools import reduce


class BaseIntegrationTest(unittest.TestCase):

    OUTPUT_FILENAME = "test_integration_out.nc"

    def setUp(self):
        # Set force overwrite in case working files are still present
        os.environ['CIS_FORCE_OVERWRITE'] = "True"
        self.clean_output()

    def tearDown(self):
        # Pop off the environemnt variable
        os.environ.pop('CIS_FORCE_OVERWRITE')
        self.clean_output()

    def clean_output(self):
        if hasattr(self, 'ds') and self.ds.isopen():
            self.ds.close()
        if os.path.exists(self.OUTPUT_FILENAME):
            os.remove(self.OUTPUT_FILENAME)

    def check_output_contains_variables(self, output_path, var_names):
        self.ds = Dataset(output_path)
        for var in var_names:
            try:
                var = self.ds.variables[var]
            except KeyError:
                raise AssertionError("Variable %s not found in output file" % var)
        self.ds.close()

    def check_output_file_variable_attribute_contains_string(self, output_path, variable, attribute, string):
        self.ds = Dataset(output_path)
        try:
            var = self.ds.variables[variable]
        except KeyError:
            raise AssertionError("Variable %s not found in output file" % variable)
        try:
            att_string = getattr(var, attribute)
        except AttributeError:
            raise AssertionError("Attribute %s not found in variable" % attribute)
        assert string in att_string
        self.ds.close()

    def check_latlon_subsetting(self, lat_max, lat_min, lon_max, lon_min, lat_var='latitude', lon_var='longitude'):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        lat = self.ds.variables[lat_var][:]
        lon = self.ds.variables[lon_var][:]
        assert_that(min(lon), greater_than_or_equal_to(lon_min))
        assert_that(max(lon), less_than_or_equal_to(lon_max))
        assert_that(min(lat), greater_than_or_equal_to(lat_min))
        assert_that(max(lat), less_than_or_equal_to(lat_max))
        self.ds.close()

    def check_alt_subsetting(self, alt_max, alt_min):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        alt = self.ds.variables['altitude'][:]
        assert_that(min(alt), greater_than_or_equal_to(alt_min))
        assert_that(max(alt), less_than_or_equal_to(alt_max))
        self.ds.close()

    def check_pres_subsetting(self, pres_max, pres_min, pres_name='air_pressure'):
        import numpy as np
        self.ds = Dataset(self.OUTPUT_FILENAME)
        pres = self.ds.variables[pres_name][:]
        assert_that(np.min(pres), greater_than_or_equal_to(pres_min))
        assert_that(np.max(pres), less_than_or_equal_to(pres_max))
        self.ds.close()

    @staticmethod
    def _clean_sample_file_name(sample_file):
        import re
        return re.sub(r'([\\]):', r':', sample_file)

    def check_output_col_grid(self, sample_file, sample_var, output_file, output_vars, expected_shape=None):
        """
        Check that the output grid matches the sample grid in shape.
        :param sample_file:
        :param sample_var:
        :param output_file:
        :param output_vars:
        :return:
        """
        from cis import read_data
        from operator import mul
        if expected_shape is None:
            sample_shape = read_data(self._clean_sample_file_name(sample_file), sample_var).data.shape
        else:
            sample_shape = expected_shape
        self.ds = Dataset(self._clean_sample_file_name(output_file))
        for output_var in output_vars:
            output_shape = self.ds.variables[output_var].shape
            # This copes with dims in different orders, length 1 values being taken out etc
            assert_that(reduce(mul, sample_shape), is_(reduce(mul, output_shape)))
        self.ds.close()

    def check_output_vars_are_different(self, output_file, output_vars):
        """
        Check that the output variables are NOT exactly the same
        :param output_file:
        :param output_vars:
        :return:
        """
        from itertools import combinations
        import numpy as np
        self.ds = Dataset(self._clean_sample_file_name(output_file))
        # Loop over each possible pair of output var
        for a, b in combinations(output_vars, 2):
            a_data = self.ds.variables[a]
            b_data = self.ds.variables[b]
            assert not np.allclose(a_data, b_data)
        self.ds.close()