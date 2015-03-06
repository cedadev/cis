import numpy
import netCDF4
from hamcrest import assert_that, is_

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
                'AOT_500 * (550.0/500)**(-1*a550to870)', '1', '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        expected_result = [0.2341039087, 0.2285401152, 0.2228799533, 0.1953746746, 0.2094051561, 0.1696889668,
                           0.3137791803, 0.2798929273, 0.1664194279, 0.1254619092, 0.1258309124, 0.1496960031,
                           0.0768447737, 0.0550896430, 0.0534543107, 0.0538315909, 0.0666742975, 0.0512935449,
                           0.0699585189, 0.0645033944]
        assert_that(calculated_result.shape, is_((3140,)))
        assert numpy.allclose(expected_result, calculated_result[0:20])

    def test_ECHAMHAM_wavelength_sum(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), '1', '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = [0.007633533, 0.007646653, 0.007749859, 0.007744226, 0.007761176]

        assert_that(calculated_result.shape, is_((96, 192)))
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
                '1', '-o', self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        calculated_result = ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = numpy.ma.masked_invalid([float('Nan'), float('Nan'), float('Nan'), 0.0004584692, 0.000697334])

        assert_that(calculated_result.shape, is_((311,)))
        compare_masked_arrays(expected_result, calculated_result[:][0:5])

    def test_CloudSat(self):
        args = ['eval', "%s,%s:%s" % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable,
                                      valid_cloudsat_RVOD_file),
                '%s/%s' % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable), 'ppm', '-o',
                'cloudsat_var:' + self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)
        ds = netCDF4.Dataset(self.UNGRIDDED_OUTPUT_FILENAME)
        assert_that(ds.variables['cloudsat_var'].units, is_('ppm'))

    def test_can_specify_output_variable(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_NAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        assert 'var_out' in ds.variables

    def test_can_specify_attributes_gridded(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_NAME, '-a', 'att1=val1,att2=val2']
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        assert_that(ds.variables['var_out'].att1, is_('val1'))
        assert_that(ds.variables['var_out'].att2, is_('val2'))

    def test_can_specify_units_gridded(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, valid_echamham_filename),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_NAME, '-a', 'att1=val1,att2=val2']
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        ds = netCDF4.Dataset(self.GRIDDED_OUTPUT_FILENAME)
        assert_that(ds.variables['var_out'].units, is_('kg m^-3'))

    def test_can_specify_units_gridded_no_output_var(self):
        args = 'eval od550aer:%s od550aer ppm -o 222 -a att1=val1' % valid_hadgem_filename
        arguments = parse_args(args.split(" "))
        evaluate_cmd(arguments)
        ds = netCDF4.Dataset('222.nc')
        assert_that(ds.variables['calculated_variable'].units, is_('ppm'))
        assert_that(ds.variables['calculated_variable'].att1, is_('val1'))
