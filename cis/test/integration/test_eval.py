import netCDF4

import numpy
from hamcrest import assert_that, is_
import unittest

from cis.cis_main import evaluate_cmd, col_cmd
from cis.test.integration.base_integration_test import BaseIntegrationTest
from cis.test.integration_test_data import *
from cis.parse import parse_args
from cis.test.unit.eval.test_calc import compare_masked_arrays


class TestEval(BaseIntegrationTest):

    def test_Aeronet_wavelength_calculation(self):
        # Example from the CIS Phase 3 Software spec:
        # ... a user should be able to write a plugin to calculate the Aeronet AOD at 550nm from the AOD at 500 nm as
        # AOD550 = AOD500 * (550/500)^(-1*Angstrom500-870)"
        # Takes 3s
        args = ['eval', 'AOT_500,500-870Angstrom=a550to870:' + escape_colons(another_valid_aeronet_filename),
                'AOT_500 * (550.0/500)**(-1*a550to870)', '1', '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        calculated_result = self.ds.variables['calculated_variable'][:]
        expected_result = [0.2341039087, 0.2285401152, 0.2228799533, 0.1953746746, 0.2094051561, 0.1696889668,
                           0.3137791803, 0.2798929273, 0.1664194279, 0.1254619092, 0.1258309124, 0.1496960031,
                           0.0768447737, 0.0550896430, 0.0534543107, 0.0538315909, 0.0666742975, 0.0512935449,
                           0.0699585189, 0.0645033944]
        assert_that(calculated_result.shape, is_((3140,)))
        assert numpy.allclose(expected_result, calculated_result[0:20])

    def test_ECHAMHAM_wavelength_sum(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, escape_colons(valid_echamham_filename)),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), '1', '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        # Check correct:
        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        calculated_result = self.ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = [0.007633533, 0.007646653, 0.007749859, 0.007744226, 0.007761176]

        assert_that(calculated_result.shape, is_((96, 192)))
        assert numpy.allclose(expected_result, calculated_result[:][0][0:5])

    def test_collocated_NetCDF_Gridded_onto_GASSP(self):
        # First do a collocation of ECHAMHAM onto GASSP
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = escape_colons(valid_echamham_filename)
        sample_file = escape_colons(valid_GASSP_aeroplane_filename)
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'nn[missing_data_for_missing_sample=True],variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':collocator=' + collocator_and_opts,
                     '-o', 'collocated_gassp']
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

        # Check collocation is the same
        self.ds = netCDF4.Dataset('collocated_gassp.nc')
        col_var1 = self.ds.variables[valid_echamham_variable_1][:]
        col_var2 = self.ds.variables[valid_echamham_variable_2][:]
        # A hand calculated selection of values
        expected_col1 = numpy.ma.masked_invalid(
            [float('Nan'), float('Nan'), float('Nan'), 0.0814601778984, 0.0814601778984])
        compare_masked_arrays(expected_col1, col_var1[:][0:5])
        expected_col2 = numpy.ma.masked_invalid(
            [float('Nan'), float('Nan'), float('Nan'), 0.0741240680218, 0.0741240680218])
        compare_masked_arrays(expected_col2, col_var2[:][0:5])

        # Then do an evaluation using the collocated data:
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2,
                                      'collocated_gassp.nc'),
                "%s=gassp_alias:%s" % (valid_GASSP_aeroplane_variable, escape_colons(valid_GASSP_aeroplane_filename)),
                "(%s + %s) / gassp_alias " % (valid_echamham_variable_1, valid_echamham_variable_2),
                '1', '-o', self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)
        self.ds.close()

        # Check correct
        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        calculated_result = self.ds.variables['calculated_variable'][:]
        # A hand calculated selection of values
        expected_result = numpy.ma.masked_invalid([0.00196121983491, 0.00197255626472, 0.00120850731992])

        assert_that(calculated_result.shape, is_((311,)))
        # Check the first 3 vald values
        compare_masked_arrays(expected_result, calculated_result[:][10:13])
        os.remove('collocated_gassp.nc')

    @skip_pyhdf
    def test_CloudSat(self):
        args = ['eval', "%s,%s:%s" % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable,
                                      escape_colons(valid_cloudsat_RVOD_file)),
                '%s/%s' % (valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable), 'ppm', '-o',
                'cloudsat_var:' + self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)
        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        assert_that(self.ds.variables['cloudsat_var'].units, is_('ppm'))

    def test_can_specify_output_variable(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, escape_colons(valid_echamham_filename)),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_FILENAME]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        assert 'var_out' in self.ds.variables

    def test_can_specify_attributes_gridded(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, escape_colons(valid_echamham_filename)),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_FILENAME, '-a', 'att1=val1,att2=val2']
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        assert_that(self.ds.variables['var_out'].att1, is_('val1'))
        assert_that(self.ds.variables['var_out'].att2, is_('val2'))

    def test_can_specify_units_gridded(self):
        args = ['eval', "%s,%s:%s" % (valid_echamham_variable_1, valid_echamham_variable_2, escape_colons(valid_echamham_filename)),
                '%s+%s' % (valid_echamham_variable_1, valid_echamham_variable_2), 'kg m^-3',
                '-o', 'var_out:' + self.OUTPUT_FILENAME, '-a', 'att1=val1,att2=val2']
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        assert_that(self.ds.variables['var_out'].units, is_('kg m^-3'))

    def test_can_specify_units_gridded_no_output_var(self):
        args = ['eval', "%s:%s" % (valid_hadgem_variable, escape_colons(valid_hadgem_filename)), "od550aer", "ppm", "-o",
                self.OUTPUT_FILENAME, "-a", "att1=val1"]
        arguments = parse_args(args)
        evaluate_cmd(arguments)

        self.ds = netCDF4.Dataset(self.OUTPUT_FILENAME)
        assert_that(self.ds.variables['calculated_variable'].units, is_('ppm'))
        assert_that(self.ds.variables['calculated_variable'].att1, is_('val1'))
