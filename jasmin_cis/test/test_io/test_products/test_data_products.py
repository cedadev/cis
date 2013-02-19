'''
module to test the various subclasses of the abstract AProduct class
'''
from nose.tools import istest, eq_, raises
from data_io.products.products import *
from jasmin_cis.exceptions import FileIOError, InvalidVariableError
from jasmin_cis.test.test_files.data import *

def check_regex_matching(cls_name, filename):
    from data_io.products.AProduct import __get_class
    cls = __get_class(filename)
    eq_(cls.__name__,cls_name)

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
    @raises(IOError)
    def should_raise_ioerror_with_invalid_filename(self):
        self.product().create_data_object([self.invalid_filename], self.valid_variable)

    @istest
    @raises(ValueError, FileIOError)
    def should_raise_valueerror_or_fileioerror_with_file_that_is_not_a_recognised_format(self):
        self.product().create_data_object([self.invalid_format], self.valid_variable)

    @istest
    @raises(InvalidVariableError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        self.product().create_data_object([self.filename], self.invalid_variable)


class TestCloudsat(ProductTests):

    def __init__(self):
        self.filename = valid_cloudsat_RVOD_file
        self.invalid_filename = "im_an_invalid_file"
        self.invalid_format = non_netcdf_file
        self.valid_variable = valid_cloudsat_RVOD_variable
        self.invalid_variable = "im_an_invalid_variable"
        self.file_without_read_permissions = file_without_read_permissions
        self.product = Cloudsat_2B_CWC_RVOD


#
# class TestMODIS_L3(ProductTests):
#     pass
#
# class TestMODIS_L2(ProductTests):
#     pass
#
# class TestCloud_CCI(ProductTests):
#     pass
#
# class TestCisCol(ProductTests):
#     pass

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
        self.filename = valid_1d_filename
        self.invalid_filename = "im_an_invalid_file"
        self.invalid_format = non_netcdf_file
        self.valid_variable = valid_variable_in_valid_filename
        self.invalid_variable = "im_an_invalid_variable"
        self.file_without_read_permissions = file_without_read_permissions
        self.product = Xglnwa_vprof


# class TestXenida(ProductTests):
#     pass
#
# class TestAeronet(ProductTests):
#     pass
