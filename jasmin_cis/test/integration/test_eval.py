import numpy
import netCDF4

from jasmin_cis.cis import evaluate_cmd, col_cmd
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest
from jasmin_cis.test.test_files.data import *
from jasmin_cis.parse import parse_args
from jasmin_cis.test.unit.eval.test_calc import compare_masked_arrays


class TestEval(BaseIntegrationTest):

    def test_Aeronet_wavelength_calculation(self):
        # Example from the CIS Phase 3 Software spec:
        # ... a user should be able to write a plugin to calculate the Aeronet AOD at 550nm from the AOD at 500 nm as
        # AOD550 = AOD500 * (550/500)^(-1*Angstrom500-870)"
        # Takes 3s
        args = ['eval', 'AOT_500,500-870Angstrom=a550to870:' + another_valid_aeronet_filename,
                'AOT_500 * (550.0/500)**(-1*a550to870)', '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        expected_result = [0.2341039087, 0.2285401152, 0.2228799533, 0.1953746746, 0.2094051561, 0.1696889668,
                           0.3137791803, 0.2798929273, 0.1664194279, 0.1254619092, 0.1258309124, 0.1496960031,
                           0.0768447737, 0.0550896430, 0.0534543107, 0.0538315909, 0.0666742975, 0.0512935449,
                           0.0699585189, 0.0645033944]
        assert calculated_result.shape == (3140,)
        assert numpy.allclose(expected_result, calculated_result[0:20])

    def test_ECHAMHAM_wavelength_sum(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = [0.007633533, 0.007646653, 0.007749859, 0.007744226, 0.007761176]

        assert calculated_result.shape == (96, 192)
        assert numpy.allclose(expected_result, calculated_result[:][0][0:5])

    def test_colocated_NetCDF_Gridded_onto_GASSP(self):
        # First do a colocation of ECHAMHAM onto GASSP
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', 'colocated_gassp']
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

        # Then do an evaluation using the colocated data:
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2,
                                      'cis-colocated_gassp.nc'),
                "%s=gassp_alias:%s" % (valid_GASSP_aeroplane_variable, valid_GASSP_aeroplane_filename),
                "(%s + %s) / gassp_alias " % (valid_echamham_variable_1, valid_echamham_variable_2),
                '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        #Check correct
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = numpy.ma.masked_invalid([float('Nan'), float('Nan'), float('Nan'), 0.0004584692, 0.000697334])

        assert calculated_result.shape == (311,)
        compare_masked_arrays(expected_result, calculated_result[:][0:5])

    def test_CloudSat(self):
        args = ['eval', "%s,%s:%s" % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable,
                                      valid_cloudsat_RVOD_file),
                '%s/%s' % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable), '-o',
                'cloudsat_var:' + self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        assert ds.variables['cloudsat_var']

    def test_can_specify_output_variable(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), '-o', 'var_out:' + self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        assert 'var_out' in ds.variables
