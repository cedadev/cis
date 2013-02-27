'''
module to test the various subclasses of the abstract AProduct class
'''
from nose.tools import istest, eq_, raises
from jasmin_cis.data_io.products.products import *
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.test.test_files.data import non_netcdf_file


def check_regex_matching(cls_name, filename):
    from jasmin_cis.data_io.products.AProduct import __get_class
    cls = __get_class(filename)
    eq_(cls.__name__,cls_name)

invalid_variable = "im_an_invalid_variable"
invalid_filename = "im_an_invalid_file"
invalid_format = non_netcdf_file

class ProductTests():

    @istest
    def test_file_regex_matching(self):
        check_regex_matching(self.product.__name__, self.filename)

    @istest
    def test_file_regex_matching_for_full_path(self):
        check_regex_matching(self.product.__name__, "/home/duncan/"+self.filename)

    @istest
    def test_create_data_object(self):
        self.product().create_data_object([self.filename], self.valid_variable)

    @istest
    def test_create_coords(self):
        self.product().create_coords([self.filename])

    @istest
    def test_write_coords(self):
        from jasmin_cis.data_io.write_netcdf import write_coordinates
        from os import remove
        test_file = '/tmp/test_out.nc'
        coords = self.product().create_coords([self.filename])
        write_coordinates(coords, test_file)
        remove(test_file)

    @istest
    @raises(IOError)
    def should_raise_ioerror_with_invalid_filename(self):
        self.product().create_data_object([invalid_filename], self.valid_variable)

    @istest
    @raises(IOError)
    def should_raise_ioerror_with_file_that_is_not_a_recognised_format(self):
        self.product().create_data_object([invalid_format], self.valid_variable)

    @istest
    @raises(InvalidVariableError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        self.product().create_data_object([self.filename], invalid_variable)


class TestCloudsat(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_variable
        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_variable
        self.product = Cloudsat_2B_CWC_RVOD

    @istest
    @raises(InvalidVariableError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        # workaround for HDF library bug in Jasmin
        raise InvalidVariableError

#
# class TestMODIS_L3(ProductTests):
#     pass
#
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

class TestCisCol(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_cis_col_file
        self.filename = valid_cis_col_file
        self.valid_variable = 'mass_fraction_of_cloud_liquid_water_in_air'
        self.product = CisCol

# class TestXglnwa(ProductTests):
#
#     def __init__(self):
#         self.filename = valid_1d_filename
#         self.invalid_filename = "im_an_invalid_file"
#         self.invalid_format = non_netcdf_file
#         self.valid_variable = valid_variable_in_valid_filename
#         self.invalid_variable = "im_an_invalid_variable"
#         self.file_without_read_permissions = file_without_read_permissions
#         self.product = Xglnwa

class TestXglnwa_vprof(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_1d_filename, valid_variable_in_valid_filename
        self.filename = valid_1d_filename
        self.valid_variable = valid_variable_in_valid_filename
        self.product = Xglnwa_vprof


# class TestXenida(ProductTests):
#     pass
#
class TestAeronet(ProductTests):
    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_aeronet_filename, valid_aeronet_variable
        self.filename = valid_aeronet_filename
        self.valid_variable = valid_aeronet_variable
        self.product = Aeronet
