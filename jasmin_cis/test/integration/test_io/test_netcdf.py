'''
module to test the NetCDF module
'''
import unittest

from netCDF4 import Variable
from hamcrest import *
from nose.tools import istest, raises, eq_

from jasmin_cis.test.test_files.integration_test_data import *
from jasmin_cis.data_io.netcdf import *


@istest
@raises(IOError)
def should_raise_io_error_with_file_that_is_not_netcdf():
    read(valid_aeronet_filename, valid_aeronet_variable)


@istest
def test_that_can_read_all_variables():
    dict = get_netcdf_file_variables(valid_2d_filename)
    eq_(len(dict), 426)


@istest
def test_that_can_read_known_variable():
    data = read(valid_2d_filename, 'latitude')
    assert (isinstance(data['latitude'], Variable))


@istest
def test_that_can_get_data():
    data = read(valid_2d_filename, 'latitude')
    eq_(data['latitude'].shape, (145,))


@istest
def test_that_can_get_metadata_for_known_variable():
    data = read(valid_2d_filename, 'rain')
    metadata = get_metadata(data['rain'])

    eq_(str(metadata.missing_value), "2e+20")
    eq_(metadata.long_name, "TOTAL RAINFALL RATE: LS+CONV KG/M2/S")
    eq_(metadata.units,
        "kg m-2 s-1")


class TestNetCDFGroups(unittest.TestCase):
    root_vars = [u'StartOrbit', u'EndOrbit', u'SpaceCraftID', u'Year', u'Month', u'Day', u'Hour', u'Minute',
                 u'DegradedInstMdr', u'DegradedProcMdr', u'GOMEScanMode']
    group_vars = {'GOME2': [u'ChannelNumber',
                            u'StartValidPixel',
                            u'EndValidPixel',
                            u'StartValidWavelengths',
                            u'EndValidWavelengths',
                            u'ChannelReadoutSeq',
                            u'BandChannelNumber',
                            u'BandNumber',
                            u'StartPixel',
                            u'NumberOfPixel',
                            u'StartLambda',
                            u'EndLambda',
                            u'StartPixelPmd',
                            u'LengthPixelPmd',
                            u'WavelengthPmd'],
                  'AVHRR': [u'Ch4CentralWavenumber',
                            u'Ch4Constant1',
                            u'Ch4Constant2Slope',
                            u'Ch5CentralWavenumber',
                            u'Ch5Constant1',
                            u'iCh5Constant2Slope',
                            u'ConstantC1',
                            u'ConstantC2'],
                  'IASI': [u'IASIFlag']}

    def _get_fully_qualified_vars(self):
        all_vars = self.root_vars
        for group, vars in self.group_vars.iteritems():
            for var in vars:
                all_vars.append(".".join([group, var]))
        return all_vars

    def test_can_get_netcdf_file_variables(self):
        all_vars = self._get_fully_qualified_vars()
        nc_vars = get_netcdf_file_variables(valid_netcdf_groups_file)
        assert_that(set(nc_vars.keys()), is_(set(all_vars)))

    def test_can_read_many_files_individually(self):
        all_vars = self._get_fully_qualified_vars()
        data = read_many_files_individually([valid_netcdf_groups_file], all_vars)
        assert_that(data[u'StartOrbit'][0][:], is_([8031]))
        assert_that(data[u'GOME2.ChannelNumber'][0][:], contains(1, 2, 3, 4, 5, 6))
        assert_that(data[u'AVHRR.Ch4CentralWavenumber'][0][:], is_([933.63]))
        assert_that(data[u'IASI.IASIFlag'][0][:], is_([0]))

    def test_can_read(self):
        all_vars = self._get_fully_qualified_vars()
        data = read(valid_netcdf_groups_file, all_vars)
        assert_that(data[u'StartOrbit'][:], is_([8031]))
        assert_that(data[u'GOME2.ChannelNumber'][:], contains(1, 2, 3, 4, 5, 6))
        assert_that(data[u'AVHRR.Ch4CentralWavenumber'][:], is_([933.63]))
        assert_that(data[u'IASI.IASIFlag'][:], is_([0]))

    def test_can_remove_variables_with_non_spatiotemporal_dimensions(self):
        nc_vars = get_netcdf_file_variables(valid_netcdf_groups_file)
        allowed_dims = ['Dim4', 'Dim7', 'Dim8']
        remove_variables_with_non_spatiotemporal_dimensions(nc_vars, allowed_dims)
        expected_vars = ['DegradedInstMdr', 'DegradedProcMdr', 'GOMEScanMode',
                         'GOME2.StartPixelPmd', 'GOME2.LengthPixelPmd', 'GOME2.WavelengthPmd']
        assert_that(nc_vars.keys(), contains_inanyorder(*expected_vars))

    def test_can_read_nested_groups(self):
        var_name = 'group1.group2.var4'
        data = read(valid_nested_groups_file, var_name)
        assert_that(data[var_name][:], is_([12321]))

    def test_can_get_variables_nested_groups(self):
        nc_vars = get_netcdf_file_variables(valid_nested_groups_file)
        expected_vars = ['var1', 'var2', 'group1.var3', 'group1.group2.var4', 'group3.var5', 'group3.group4.var6']
        assert_that(nc_vars.keys(), contains_inanyorder(*expected_vars))
