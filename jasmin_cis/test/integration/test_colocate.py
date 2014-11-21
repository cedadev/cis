import unittest

from jasmin_cis.cis import col_cmd
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *


class TestUngriddedGriddedColocate(BaseIntegrationTest):

    def test_GIVEN_single_variable_WHEN_colocate_THEN_successful_colocation(self):
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        sample_file = valid_hadgem_filename
        colocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['ATX'])

    def test_GIVEN_multiple_variables_on_same_coords_WHEN_colocate_THEN_successful_colocation(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        colocator_and_opts = 'bin,kernel=mean,variable=TAU_2D_550nm'
        arguments = ['col', variable1 + ',' + variable2 + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD550'])
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD870'])

    def test_GIVEN_multiple_datagroups_on_same_coords_WHEN_colocate_THEN_successful_colocation(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        colocator_and_opts = 'bin,kernel=mean,variable=TAU_2D_550nm'
        arguments = ['col', variable1 + ':' + filename,
                     variable2 + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD550'])
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD870'])

if __name__ == '__main__':
    unittest.main()
