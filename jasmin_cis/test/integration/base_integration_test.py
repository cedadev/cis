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

    def check_output_col_grid(self, sample_file, sample_var, output_file, output_vars):
        """
        Check that the output grid matches the sample grid in shape.
        :param sample_file:
        :param sample_var:
        :param output_file:
        :param output_vars:
        :return:
        """
        from netCDF4 import Dataset
        sample_shape = None
        if sample_file.endswith('.nc'):
            sample = Dataset(sample_file)
            sample_shape = sample.variables[sample_var].shape
        elif sample_file.endswith('.hdf'):
            from pyhdf.SD import SD
            sd = SD(sample_file)
            svars = sd.datasets()
            if sample_var in svars:
                sample_shape = svars[sample_var][1]
            else:
                from pyhdf.HDF import HDF
                from pyhdf.VS import VS
                hdf = HDF(sample_file)
                vs = hdf.vstart()
                for info in vs.vdatainfo():
                    if info[0] == sample_var:
                        sample_shape = (info[3],)
        elif sample_file.endswith('.lev20') or sample_file.endswith('.txt'):
            f = open(sample_file)
            line_count = - 5  # Aeronet headers are five lines.
            for line in f:
                if line.strip():
                    line_count += 1
            sample_shape = (line_count,)
        output = Dataset(output_file)
        for output_var in output_vars:
            output_shape = output.variables[output_var].shape
            try:
                assert sample_shape == output_shape
            except AssertionError:
                try:
                    # Sometimes there is a dimension which is flattened out, try just lat lon
                    assert sample_shape[-2:] == output_shape
                except AssertionError:
                    # If the data gets flattened (MODIS L3 I think?) then check with the number of points
                    assert output_shape == (sample_shape[-1] * sample_shape[-2],)