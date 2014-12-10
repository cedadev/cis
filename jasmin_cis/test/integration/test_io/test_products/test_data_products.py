"""
module to test the various subclasses of the abstract AProduct class
"""
from nose.tools import istest, eq_, raises, nottest
from iris.exceptions import TranslationError

from data_io.products.NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from data_io.products.products import *
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.test.test_files.data import non_netcdf_file


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
    valid_variable = None

    @istest
    def test_file_regex_matching(self):
        check_regex_matching(self.product.__name__, self.filename)

    @istest
    def test_file_regex_matching_for_full_path(self):
        check_regex_matching(self.product.__name__, "/home/duncan/"+self.filename)
        check_regex_matching(self.product.__name__, "/a/xenida/more/lev20/confusing/hdf/path/nc/"+self.filename)

    @istest
    def test_create_data_object(self):
        self.product().create_data_object([self.filename], self.valid_variable)

    @istest
    def test_create_coords(self):
        valid_standard_names = ['latitude', 'longitude', 'altitude', 'time', 'air_pressure']
        coords = self.product().create_coords([self.filename], self.valid_variable)
        coord_list = coords.coords()

        for coord in coord_list:
            logging.debug(coord.standard_name)

        for coord in coord_list:
            print coord.standard_name

        assert(all([coord.standard_name in valid_standard_names for coord in coord_list]))

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


class TestCloudsatRVODsdata(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_sdata_variable
        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_sdata_variable
        self.product = CloudSat


class TestCloudsatRVODvdata(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_vdata_variable
        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_vdata_variable
        self.product = CloudSat


class TestCloudsatPRECIP(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_PRECIP_file, valid_cloudsat_PRECIP_variable
        self.filename = valid_cloudsat_PRECIP_file
        self.valid_variable = valid_cloudsat_PRECIP_variable
        self.product = CloudSat


class TestMODIS_L3(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_modis_l3_filename, valid_modis_l3_variable
        self.filename = valid_modis_l3_filename
        self.valid_variable = valid_modis_l3_variable
        self.product = MODIS_L3


class TestCaliop_L2(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_caliop_l2_filename, valid_caliop_l2_variable
        self.filename = valid_caliop_l2_filename
        self.valid_variable = valid_caliop_l2_variable
        self.product = Caliop_L2


class TestCaliop_L1(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_caliop_l1_filename, valid_caliop_l1_variable
        self.filename = valid_caliop_l1_filename
        self.valid_variable = valid_caliop_l1_variable
        self.product = Caliop_L1


class TestMODIS_L2(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_modis_l2_filename, valid_modis_l2_variable
        self.filename = valid_modis_l2_filename
        self.valid_variable = valid_modis_l2_variable
        self.product = MODIS_L2


class TestCloud_CCI(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cloud_cci_filename, valid_cloud_cci_variable
        self.filename = valid_cloud_cci_filename
        self.valid_variable = valid_cloud_cci_variable
        self.product = Cloud_CCI


class TestAerosol_CCI(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_aerosol_cci_filename, valid_aerosol_cci_variable
        self.filename = valid_aerosol_cci_filename
        self.valid_variable = valid_aerosol_cci_variable
        self.product = Aerosol_CCI


class TestCis(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cis_col_file
        self.filename = valid_cis_col_file
        self.valid_variable = 'AOT_440'
        self.product = cis


class TestAeronet(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_aeronet_filename, valid_aeronet_variable, another_valid_aeronet_filename
        self.filename = valid_aeronet_filename
        self.filenames = [valid_aeronet_filename, another_valid_aeronet_filename]
        self.valid_variable = valid_aeronet_variable
        self.product = Aeronet

    @istest
    def test_create_data_object_from_multiple_files(self):
        self.product().create_data_object(self.filenames, self.valid_variable)


class TestASCII(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_ascii_filename, valid_ascii_variable, ascii_filename_with_no_values
        self.filename = valid_ascii_filename
        self.no_value_filename = ascii_filename_with_no_values
        self.valid_variable = valid_ascii_variable
        self.product = ASCII_Hyperpoints

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
        assert(all(data.data.mask == [False, False, False, True, False, True, False, False]))

    @istest
    def test_create_data_object_with_valid_datetime(self):
        import datetime
        from jasmin_cis.time_util import convert_datetime_to_std_time
        data = self.product().create_data_object([self.filename], True)
        assert(data.coord('time').data[3] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 25, 15, 32, 03)))
        assert(data.coord('time').data[4] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 26)))


class TestNetCDF_Gridded_xenida(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_xenida_filename, valid_xenida_variable
        self.filename = valid_xenida_filename
        self.valid_variable = valid_xenida_variable
        self.product = default_NetCDF

    #TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass


class TestNetCDF_Gridded_xglnwa(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_1d_filename, valid_1d_variable
        self.filename = valid_1d_filename
        self.valid_variable = valid_1d_variable
        self.product = default_NetCDF

    #TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass
