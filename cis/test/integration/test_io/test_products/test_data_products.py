"""
module to test the various subclasses of the abstract AProduct class
"""

import unittest
import logging
import os
from tempfile import mkdtemp

from hamcrest import *
from nose.tools import istest, eq_, raises, nottest, with_setup, assert_is_instance

from cis.data_io.products import *
from cis.exceptions import InvalidVariableError, FileFormatError
from cis.test.integration_test_data import non_netcdf_file, cis_test_files, skip_pyhdf
from cis.data_io.products import CloudSat

try:
    import pandas
except ImportError:
    # Disable all these tests if pandas is not installed.
    pandas = None

skip_pandas = unittest.skipIf(pandas is None, 'Test(s) require "pandas", which is not available.')


def check_regex_matching(cls_name, filename):
    from cis.data_io.products.AProduct import __get_class
    cls = __get_class(filename)
    eq_(cls.__name__, cls_name)

invalid_variable = "im_an_invalid_variable"
invalid_filename = "im_an_invalid_file"
invalid_format = non_netcdf_file

test_file = os.path.join(mkdtemp('cis_test_dir'), 'test_out.nc')


def remove_test_file():
    """
        Try and remove the test file if it exists
    :return:
    """
    from os import remove
    from os.path import isfile
    if isfile(test_file):
        remove(test_file)


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
        from cis.test.integration_test_data import TestFileTestData
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

    @istest
    def test_variable_printing(self):
        import six
        data_obj = self.product().create_data_object([self.filename], self.valid_variable)
        summary = data_obj.summary()
        assert_is_instance(summary, six.string_types)

    def check_valid_vars(self, vars):
        if self.vars is not None:
            assert_that(set(vars), is_(set(self.vars)), "Variables")
        else:
            assert_that(len(vars), is_(self.valid_vars_count), "Number of valid variables in the file")

    def test_create_data_object(self):
        from cis.data_io.common_data import CommonData
        data = self.product().create_data_object([self.filename], self.valid_variable)
        assert_is_instance(data, CommonData)

    @skip_pandas
    def test_create_pandas_object(self):
        from pandas import DataFrame
        data = self.product().create_data_object([self.filename], self.valid_variable)
        df = data.as_data_frame()
        assert_is_instance(df, DataFrame)

    def test_create_coords(self):
        valid_standard_names = ['latitude', 'longitude', 'altitude', 'time', 'air_pressure']
        coords = self.product().create_coords([self.filename])
        coord_list = coords.coords()

        for coord in coord_list:
            logging.debug(coord.standard_name)

        assert (all([coord.standard_name in valid_standard_names for coord in coord_list]))

    @with_setup(remove_test_file, remove_test_file)
    def test_write_coords(self):
        from cis.data_io.write_netcdf import write_coordinates
        coords = self.product().create_coords([self.filename], self.valid_variable)
        write_coordinates(coords, test_file)

    @raises(IOError)
    def test_should_raise_ioerror_with_invalid_filename(self):
        self.product().create_data_object([invalid_filename], self.valid_variable)

    @raises(IOError, FileFormatError)
    def test_should_raise_ioerror_or_translationerror_with_file_that_is_not_a_recognised_format(self):
        self.product().create_data_object([invalid_format], self.valid_variable)

    @raises(InvalidVariableError)
    def test_should_raise_error_when_variable_does_not_exist_in_file(self):
        self.product().create_data_object([self.filename], invalid_variable)

    def test_file_format(self):
        expected_file_format = self.file_format
        if expected_file_format is None:
            expected_file_format = self.product.__name__
        file_format = self.product().get_file_format(self.filename)
        assert_that(file_format, is_(expected_file_format), "File format")


@skip_pyhdf
class TestCloudsatRVODsdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_sdata_variable, \
            valid_cloudsat_RVOD_file_format

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_sdata_variable
        self.product = CloudSat
        self.file_format = valid_cloudsat_RVOD_file_format

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


@skip_pyhdf
class TestCloudsatRVODvdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_vdata_variable, \
            valid_cloudsat_RVOD_file_format

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_vdata_variable
        self.product = CloudSat
        self.file_format = valid_cloudsat_RVOD_file_format

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


@skip_pyhdf
class TestCloudsatPRECIP(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_cloudsat_PRECIP_file, valid_cloudsat_PRECIP_variable, \
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



@skip_pyhdf
class TestCaliop_L2(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["caliop_L2"], Caliop_L2)


@skip_pyhdf
class TestCaliop_L1(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["caliop_L1"], Caliop_L1)


@skip_pyhdf
class TestMODIS_L3(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["modis_L3"], MODIS_L3)

    def check_valid_vars(self, vars):
        assert len(vars) == 700

    @nottest
    def test_write_coords(self):
        # Model data is gridded so IRIS takes care of this
        pass

    @nottest
    def test_create_pandas_object(self):
        # Cannot create pandas objects for data with > 2 dimensions
        pass


@skip_pyhdf
class TestMODIS_L2(ProductTests, unittest.TestCase):
    def setUp(self):

        self.setup(cis_test_files["modis_L2"], MODIS_L2)


class TestCloud_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["Cloud_CCI"], Cloud_CCI_L2)


class TestAerosol_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["Aerosol_CCI"], Aerosol_CCI_L2)

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
        from cis.test.integration_test_data import valid_aeronet_filename, another_valid_aeronet_filename
        self.setup(cis_test_files["aeronet"], Aeronet)
        self.filenames = [valid_aeronet_filename, another_valid_aeronet_filename]
        self.file_format = "ASCIIAERONET/2"

    @istest
    def test_create_data_object_from_multiple_files(self):
        self.product().create_data_object(self.filenames, self.valid_variable)


class TestASCII(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import ascii_filename_with_no_values
        self.setup(cis_test_files["ascii"], ASCII_Hyperpoints)
        self.no_value_filename = ascii_filename_with_no_values

    @raises(IOError)
    def test_should_raise_error_when_variable_does_not_exist_in_file(self):
        """
         This product throws an IO error rather than an InvalidVariable error as the file can only have one variable
        :return:
        """
        self.product().create_data_object([self.no_value_filename], True)

    @istest
    def test_create_data_object_with_missing_values(self):
        """
         Check that missing values get masked correctly
        :return:
        """
        data = self.product().create_data_object([self.filename], True)
        assert (all(data.data.mask == [False, False, False, True, False, True, False, False]))

    @istest
    def test_create_data_object_with_valid_datetime(self):
        import datetime
        from cis.time_util import convert_datetime_to_std_time

        data = self.product().create_data_object([self.filename], True)
        assert(data.coord('time').data[3] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 25, 15, 32, 0o3)))
        assert(data.coord('time').data[4] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 26)))


class TestNetCDF_Gridded_xenida(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_xenida_filename, valid_xenida_variable

        self.filename = valid_xenida_filename
        self.valid_variable = valid_xenida_variable
        self.product = NetCDF_Gridded
        self.file_format = "NetCDF/Gridded"

    @nottest
    def test_variable_wildcarding(self):
        # There are no valid variables in this file.
        pass

    @nottest
    def test_write_coords(self):
        # Model data is gridded so IRIS takes care of this
        pass

    @nottest
    def test_create_coords(self):
        # Model data is gridded so IRIS takes care of this
        pass

    @nottest
    def test_create_pandas_object(self):
        # This is broken - but it's in Iris
        pass


class TestNetCDF_Gridded_xglnwa(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_1d_filename, valid_1d_variable

        self.filename = valid_1d_filename
        self.valid_variable = valid_1d_variable
        self.product = NetCDF_Gridded
        self.file_format = "NetCDF/Gridded"

    @nottest
    def test_variable_wildcarding(self):
        # Not tested
        pass

    @nottest
    def test_write_coords(self):
        # Model data is gridded so IRIS takes care of this
        pass

    @nottest
    def test_create_coords(self):
        # Model data is gridded so IRIS takes care of this
        pass

    @nottest
    def test_create_pandas_object(self):
        # This is broken - but it's in Iris
        pass


class TestNetCDF_Gridded_HadGEM(ProductTests, unittest.TestCase):
    def setUp(self):
        from cis.test.integration_test_data import valid_hadgem_filename, valid_hadgem_variable

        self.filename = valid_hadgem_filename
        self.valid_variable = valid_hadgem_variable
        self.product = NetCDF_Gridded
        self.vars = ['od550aer']
        self.file_format = "NetCDF/Gridded"

    @nottest
    def test_write_coords(self):
        # Gridded coordinates are taken care of by IRIS
        pass

    @nottest
    def test_create_pandas_object(self):
        # Cannot create pandas objects for data with > 2 dimensions
        pass

