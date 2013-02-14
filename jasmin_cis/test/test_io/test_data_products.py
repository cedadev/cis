'''
module to test the various subclasses of the abstract AProduct class
'''
from nose.tools import istest, eq_, raises, nottest
import re
from jasmin_cis.test.test_files.data import *
from data_io.products.AProduct import get_data, __get_class
from jasmin_cis.exceptions import ClassNotFoundError
from data_io.products.products import *

@istest
def test_that_get_data_accepts_valid_product():
    __get_class([valid_cloudsat_RVOD_file], product='Cloudsat_2B_CWC_RVOD')

@istest
def test_automatic_detection_of_product_for_existing_product():
    product_cls = __get_class([valid_cloudsat_RVOD_file])
    eq_(product_cls.__name__,'Cloudsat_2B_CWC_RVOD')

    product_cls = __get_class([valid_1d_filename])
    eq_(product_cls.__name__,'NetCDF_CF_Gridded')

    # only the first file name is used for automatic detection
    product_cls = __get_class([valid_1d_filename, valid_cloudsat_RVOD_file])
    eq_(product_cls.__name__,'NetCDF_CF_Gridded')

@istest
@raises(ClassNotFoundError)
def test_that_get_class_raises_ClassNotFoundError_for_non_existing_product():
    product_cls = __get_class(['some_file_that_does_not_match_anything'])

@istest
@raises(ClassNotFoundError)
def test_that_get_data_raises_ClassNotFoundError_for_missing_product():
    get_data(valid_cloudsat_RVOD_file,[valid_cloudsat_RVOD_variable], product='Product_Not_Yet_Implemented')

@istest
@raises(TypeError)
def test_that_get_data_throws_TypeError_for_invalid_product():
    from data_io.products.AProduct import AProduct
    # Create a class which subclasses AProduct but doesn't fully implement the interface
    class My_test_product(AProduct): pass
    get_data(valid_cloudsat_RVOD_file,[valid_cloudsat_RVOD_variable], product='My_test_product')

@istest
def test_that_cloudsat_file_regex_matching():
    cls = __get_class([valid_cloudsat_RVOD_file])
    eq_(cls.__name__,'Cloudsat_2B_CWC_RVOD')

@nottest
def test_that_cci_file_regex_matching():
    pass

@nottest
def test_that_aeronet_file_regex_matching():
    pass