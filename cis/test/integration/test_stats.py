import unittest

from cis.parse import parse_args
from cis.cis_main import stats_cmd, col_cmd
from cis.test.integration_test_data import *
from cis.test.integration.base_integration_test import BaseIntegrationTest


class TestStats(BaseIntegrationTest):

    output_vars = [
        "num_points",
        "dataset_mean_1",
        "dataset_mean_2",
        "dataset_stddev_1",
        "dataset_stddev_2",
        "abs_mean",
        "abs_stddev",
        "rel_mean",
        "rel_stddev",
        "spearman",
        "regression_gradient",
        "regression_intercept",
        "regression_r",
        "regression_stderr"]

    def test_Aeronet_wavelength_stats(self):
        # Takes 3s
        args = ['stats', '%s,%s:%s' % ('AOT_500', 'AOT_440', escape_colons(another_valid_aeronet_filename)),
                '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        stats_cmd(arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, self.output_vars)

    def test_no_output_file(self):
        # Takes 3s
        args = ['stats', '%s,%s:%s' % ('AOT_500', 'AOT_440', escape_colons(another_valid_aeronet_filename))]
        arguments = parse_args(args)
        stats_cmd(arguments)

    def test_ECHAMHAM_wavelength_stats(self):
        # Takes 0.7s
        args = ['stats', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, escape_colons(valid_echamham_filename)),
                '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        stats_cmd(arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, self.output_vars)

    def test_collocated_NetCDF_Gridded_onto_GASSP(self):
        # Takes 2s
        # First do a collocation of ECHAMHAM onto GASSP
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', '%s:%s' % (valid_echamham_variable_1, escape_colons(valid_echamham_filename)),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', 'collocated_gassp']
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

        # Then do a statistics calculation using the collocated data:
        args = ['stats', "%s:%s" % (valid_echamham_variable_1, 'collocated_gassp.nc'),
                "%s:%s" % (valid_GASSP_aeroplane_variable, escape_colons(valid_GASSP_aeroplane_filename)),
                '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        stats_cmd(arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, self.output_vars)
        os.remove('collocated_gassp.nc')

    @skip_pyhdf
    def test_CloudSat(self):
        # Takes 140s
        args = ['stats', "%s,%s:%s" % ("RVOD_liq_water_content", "RVOD_ice_water_content",
                                       escape_colons(valid_cloudsat_RVOD_file)),
                '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        stats_cmd(arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, self.output_vars)


if __name__ == '__main__':
    unittest.main()
