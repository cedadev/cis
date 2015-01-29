"""
module to test the various subclasses of the abstract AProduct class
"""

import unittest
import logging

from hamcrest import *
from nose.tools import istest, eq_, raises, nottest
from iris.exceptions import TranslationError

from jasmin_cis.data_io.products import *
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.test.test_files.data import non_netcdf_file, cis_test_files


def check_regex_matching(cls_name, filename):
    from jasmin_cis.data_io.products.AProduct import __get_class
    cls = __get_class(filename)
    eq_(cls.__name__, cls_name)

invalid_variable = "im_an_invalid_variable"
invalid_filename = "im_an_invalid_file"
invalid_format = non_netcdf_file


class ProductTests(object):
    product = None
    filename = None
    vars = None
    valid_variable = None
    file_format = None
    test_file_metadata = None
    valid_vars_count = None

    @nottest
    def setup(self, test_file_metadata, product):
        from jasmin_cis.test.test_files.data import TestFileTestData
        assert isinstance(test_file_metadata, TestFileTestData)
        self.filename = test_file_metadata.master_filename
        self.valid_variable = test_file_metadata.data_variable_name
        self.vars = test_file_metadata.all_variable_names
        self.valid_vars_count = test_file_metadata.valid_vars_count
        self.file_format = test_file_metadata.file_format
        self.test_file_metadata = test_file_metadata
        self.product = product

    @istest
    def test_file_regex_matching(self):
        check_regex_matching(self.product.__name__, self.filename)

    @istest
    def test_file_regex_matching_for_full_path(self):
        import os
        check_regex_matching(self.product.__name__,  os.path.join(os.getcwd(), self.filename))

    @istest
    def test_variable_wildcarding(self):
        vars = self.product().get_variable_names([self.filename])
        self.check_valid_vars(vars)

    def check_valid_vars(self, vars):
        if self.vars is not None:
            assert_that(set(vars), is_(set(self.vars)), "Variables")
        else:
            assert_that(len(vars), is_(self.valid_vars_count ), "Number of valid variables in the file")

    @istest
    def test_create_data_object(self):
        self.product().create_data_object([self.filename], self.valid_variable)

    @istest
    def test_create_coords(self):
        valid_standard_names = ['latitude', 'longitude', 'altitude', 'time', 'air_pressure']
        coords = self.product().create_coords([self.filename])
        coord_list = coords.coords()

        for coord in coord_list:
            logging.debug(coord.standard_name)

        for coord in coord_list:
            print coord.standard_name

        assert (all([coord.standard_name in valid_standard_names for coord in coord_list]))

    @istest
    def test_write_coords(self):
        from jasmin_cis.data_io.write_netcdf import write_coordinates
        from os import remove
        test_file = '/tmp/test_out.nc'
        coords = self.product().create_coords([self.filename], self.valid_variable)
        write_coordinates(coords, test_file)
        remove(test_file)

    @istest
    @raises(IOError)
    def should_raise_ioerror_with_invalid_filename(self):
        self.product().create_data_object([invalid_filename], self.valid_variable)

    @istest
    @raises(IOError, TranslationError)
    def should_raise_ioerror_or_translationerror_with_file_that_is_not_a_recognised_format(self):
        self.product().create_data_object([invalid_format], self.valid_variable)

    @istest
    @raises(InvalidVariableError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        self.product().create_data_object([self.filename], invalid_variable)

    @istest
    def test_file_format(self):
        expected_file_format = self.file_format
        if expected_file_format is None:
            expected_file_format = self.product.__name__
        file_format = self.product().get_file_format(self.filename)
        assert_that(file_format, is_(expected_file_format), "File format")

class TestCloudsatRVODsdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_sdata_variable, \
            valid_cloudsat_RVOD_file_format

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_sdata_variable
        self.product = CloudSat
        self.file_format = valid_cloudsat_RVOD_file_format

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


class TestCloudsatRVODvdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_vdata_variable, \
            valid_cloudsat_RVOD_file_format

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_vdata_variable
        self.product = CloudSat
        self.file_format = valid_cloudsat_RVOD_file_format

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


class TestCloudsatPRECIP(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_PRECIP_file, valid_cloudsat_PRECIP_variable, \
            valid_cloudsat_PRECIP_file_format

        self.filename = valid_cloudsat_PRECIP_file
        self.valid_variable = valid_cloudsat_PRECIP_variable
        self.product = CloudSat
        self.file_format = valid_cloudsat_PRECIP_file_format
        self.vars = ['Profile_time',
                     'Latitude',
                     'Longitude',
                     'DEM_elevation',
                     'Data_quality',
                     'Data_status',
                     'Data_targetID',
                     'Precip_rate',
                     'Precip_rate_min',
                     'Precip_rate_max',
                     'Precip_rate_no_ms',
                     'PIA_hydrometeor',
                     'PIA_near_surface',
                     'Sigma_zero',
                     'Near_surface_reflectivity',
                     'Cloud_top_lowest_layer',
                     'Cloud_top_highest_layer',
                     'Frozen_precip_height',
                     'Melted_fraction',
                     'Status_flag',
                     'Precip_flag',
                     'Retrieval_info_flag',
                     'Phase_flag',
                     'Cloud_flag',
                     'SRT_flag',
                     'Surface_type',
                     'Freezing_level',
                     'SST',
                     'Surface_wind',
                     'Aux_CWV_AMSR',
                     'Aux_LWP_AMSR',
                     'Aux_SST_AMSR',
                     'Aux_precip_AMSR',
                     'Aux_dist_AMSR']


class TestCaliop_L2(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["caliop_L2"], Caliop_L2)


class TestCaliop_L1(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["caliop_L1"], Caliop_L1)


class TestMODIS_L3(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["modis_L3"], MODIS_L3)

    def check_valid_vars(self, vars):
        assert len(vars) == 700

class TestMODIS_L2(ProductTests, unittest.TestCase):
    def setUp(self):

        self.setup(cis_test_files["modis_L2"], MODIS_L2)


class TestCloud_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["Cloud_CCI"], Cloud_CCI)


class TestAerosol_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["Aerosol_CCI"], Aerosol_CCI)

    def check_valid_vars(self, vars):
        exclude_vars = ["sun_zenith", "satellite_zenith", "relative_azimuth", "instrument_view"]
        assert len(vars) == 32
        for key in exclude_vars:
            assert key not in vars


class TestCis(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["CIS_Ungridded"], cis)

class TestAeronet(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_aeronet_filename, valid_aeronet_variable, another_valid_aeronet_filename
        self.setup(cis_test_files["aeronet"], Aeronet)
        self.filenames = [valid_aeronet_filename, another_valid_aeronet_filename]

    @istest
    def test_create_data_object_from_multiple_files(self):
        self.product().create_data_object(self.filenames, self.valid_variable)


class TestASCII(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import ascii_filename_with_no_values
        self.setup(cis_test_files["ascii"], ASCII_Hyperpoints)
        self.no_value_filename = ascii_filename_with_no_values

    @istest
    @raises(IOError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        '''
         This product throws an IO error rather than an InvalidVariable error as the file can only have one variable
        :return:
        '''
        self.product().create_data_object([self.no_value_filename], True)

    @istest
    def test_create_data_object_with_missing_values(self):
        '''
         Check that missing values get masked correctly
        :return:
        '''
        data = self.product().create_data_object([self.filename], True)
        assert (all(data.data.mask == [False, False, False, True, False, True, False, False]))

    @istest
    def test_create_data_object_with_valid_datetime(self):
        import datetime
        from jasmin_cis.time_util import convert_datetime_to_std_time

        data = self.product().create_data_object([self.filename], True)
        assert(data.coord('time').data[3] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 25, 15, 32, 03)))
        assert(data.coord('time').data[4] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 26)))


class TestNetCDF_Gridded_xenida(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_xenida_filename, valid_xenida_variable

        self.filename = valid_xenida_filename
        self.valid_variable = valid_xenida_variable
        self.product = default_NetCDF
        self.file_format = "NetCDF/Gridded"

    @nottest
    def test_variable_wildcarding(self):
        # There are no valid variables in this file.
        pass

    # TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass


class TestNetCDF_Gridded_xglnwa(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_1d_filename, valid_1d_variable

        self.filename = valid_1d_filename
        self.valid_variable = valid_1d_variable
        self.product = default_NetCDF
        self.file_format = "NetCDF/Gridded"

    @nottest
    def test_variable_wildcarding(self):
        # Not tested
        pass

    # TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass


class TestNetCDF_Gridded_HadGEM(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_hadgem_filename, valid_hadgem_variable

        self.filename = valid_hadgem_filename
        self.valid_variable = valid_hadgem_variable
        self.product = default_NetCDF
        self.vars = ['od550aer']
        self.file_format = "NetCDF/Gridded"
