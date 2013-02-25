'''
module to test the abstract AProduct class and it's helper methods
'''
from nose.tools import istest, eq_, raises, nottest
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.products.AProduct import get_data, __get_class
from jasmin_cis.exceptions import ClassNotFoundError

@istest
def test_that_get_data_accepts_valid_product():
    __get_class(valid_cloudsat_RVOD_file, product='Cloudsat_2B_CWC_RVOD')

@istest
def test_automatic_detection_of_product_for_existing_product():
    product_cls = __get_class(valid_cloudsat_RVOD_file)
    eq_(product_cls.__name__,'Cloudsat_2B_CWC_RVOD')

    product_cls = __get_class(valid_1d_filename)
    eq_(product_cls.__name__,'Xglnwa_vprof')

@istest
@raises(ClassNotFoundError)
def test_that_get_class_raises_ClassNotFoundError_for_non_existing_product():
    product_cls = __get_class('some_file_that_does_not_match_anything')

@istest
@raises(ClassNotFoundError)
def test_that_get_data_raises_ClassNotFoundError_for_missing_product():
    get_data(valid_cloudsat_RVOD_file,[valid_cloudsat_RVOD_variable], product='Product_Not_Yet_Implemented')

@istest
@raises(TypeError)
def test_that_get_data_throws_TypeError_for_invalid_product():
    from jasmin_cis.data_io.products.AProduct import AProduct
    # Create a class which subclasses AProduct but doesn't fully implement the interface
    class My_test_product(AProduct): pass
    my_product = My_test_product()
