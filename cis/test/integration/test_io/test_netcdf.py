"""
module to test the NetCDF module
"""
import unittest
from netCDF4 import Variable

from hamcrest import *
from nose.tools import istest, raises, eq_

from cis.test.integration_test_data import *
from cis.data_io.netcdf import *

class TestNetCDF(unittest.TestCase):

    @raises(IOError)
    def should_raise_io_error_with_file_that_is_not_netcdf(self):
        read(valid_aeronet_filename, valid_aeronet_variable)

    def test_that_can_read_all_variables(self):
        dict = get_netcdf_file_variables(valid_2d_filename)
        eq_(len(dict), 426)

    def test_that_can_read_known_variable(self):
        data = read(valid_2d_filename, 'latitude')
        assert (isinstance(data['latitude'], Variable))

    def test_that_can_get_data(self):
        data = read(valid_2d_filename, 'latitude')
        eq_(data['latitude'].shape, (145,))

    def test_that_can_get_metadata_for_known_variable(self):
        data = read(valid_2d_filename, 'rain')
        metadata = get_metadata(data['rain'])

        eq_(str(metadata.missing_value), "2e+20")
        eq_(metadata.long_name, "TOTAL RAINFALL RATE: LS+CONV KG/M2/S")
        eq_(metadata.units,
            "kg m-2 s-1")

    def test_that_respect_valid_range_metadata(self):
        data = read(netcdf_cf_compliant_ranges_filename, netcdf_cf_compliant_ranges_vars)

        valid_min_data_array = get_data(data["CL_1944"])
        valid_min = data["CL_1944"].valid_min

        assert valid_min_data_array.min() >= valid_min

        valid_max_data_array = get_data(data["SO4_1950"])
        valid_max = data["SO4_1950"].valid_max

        assert valid_max_data_array.max() <= valid_max

        valid_range_data_array = get_data(data["LON_502"])
        valid_range = data["LON_502"].valid_range

        assert valid_range_data_array.min() >= valid_range[0]
        assert valid_range_data_array.max() <= valid_range[1]


class TestNetCDFGroups(unittest.TestCase):
    root_vars = ['StartOrbit', 'EndOrbit', 'SpaceCraftID', 'Year', 'Month', 'Day', 'Hour', 'Minute',
                 'DegradedInstMdr', 'DegradedProcMdr', 'GOMEScanMode']
    group_vars = {'GOME2': ['ChannelNumber',
                            'StartValidPixel',
                            'EndValidPixel',
                            'StartValidWavelengths',
                            'EndValidWavelengths',
                            'ChannelReadoutSeq',
                            'BandChannelNumber',
                            'BandNumber',
                            'StartPixel',
                            'NumberOfPixel',
                            'StartLambda',
                            'EndLambda',
                            'StartPixelPmd',
                            'LengthPixelPmd',
                            'WavelengthPmd'],
                  'AVHRR': ['Ch4CentralWavenumber',
                            'Ch4Constant1',
                            'Ch4Constant2Slope',
                            'Ch5CentralWavenumber',
                            'Ch5Constant1',
                            'iCh5Constant2Slope',
                            'ConstantC1',
                            'ConstantC2'],
                  'IASI': ['IASIFlag']}

    def _get_fully_qualified_vars(self):
        all_vars = self.root_vars
        for group, vars in self.group_vars.items():
            for var in vars:
                all_vars.append("/".join([group, var]))
        return all_vars

    def test_can_get_netcdf_file_variables(self):
        all_vars = self._get_fully_qualified_vars()
        nc_vars = get_netcdf_file_variables(valid_netcdf_groups_file)
        assert_that(set(nc_vars.keys()), is_(set(all_vars)))

    def test_can_read_many_files_individually(self):
        all_vars = self._get_fully_qualified_vars()
        data = read_many_files_individually([valid_netcdf_groups_file], all_vars)
        assert_that(data['StartOrbit'][0][:], is_([8031]))
        assert_that(data['GOME2/ChannelNumber'][0][:], contains(1, 2, 3, 4, 5, 6))
        assert_that(data['AVHRR/Ch4CentralWavenumber'][0][:], is_([933.63]))
        assert_that(data['IASI/IASIFlag'][0][:], is_([0]))

    def test_can_read(self):
        all_vars = self._get_fully_qualified_vars()
        data = read(valid_netcdf_groups_file, all_vars)
        assert_that(data['StartOrbit'][:], is_([8031]))
        assert_that(data['GOME2/ChannelNumber'][:], contains(1, 2, 3, 4, 5, 6))
        assert_that(data['AVHRR/Ch4CentralWavenumber'][:], is_([933.63]))
        assert_that(data['IASI/IASIFlag'][:], is_([0]))

    def test_can_remove_variables_with_non_spatiotemporal_dimensions(self):
        nc_vars = get_netcdf_file_variables(valid_netcdf_groups_file)
        allowed_dims = ['Dim4', 'Dim7', 'Dim8']
        remove_variables_with_non_spatiotemporal_dimensions(nc_vars, allowed_dims)
        expected_vars = ['DegradedInstMdr', 'DegradedProcMdr', 'GOMEScanMode',
                         'GOME2/StartPixelPmd', 'GOME2/LengthPixelPmd', 'GOME2/WavelengthPmd']
        assert_that(list(nc_vars.keys()), contains_inanyorder(*expected_vars))

    def test_can_read_nested_groups(self):
        var_name = 'group1/group2/var4'
        data = read(valid_nested_groups_file, var_name)
        assert_that(data[var_name][:], is_([12321]))

    def test_can_get_variables_nested_groups(self):
        nc_vars = get_netcdf_file_variables(valid_nested_groups_file)
        expected_vars = ['var1', 'var2', 'group1/var3', 'group1/group2/var4', 'group3/var5', 'group3/group4/var6']
        assert_that(list(nc_vars.keys()), contains_inanyorder(*expected_vars))
