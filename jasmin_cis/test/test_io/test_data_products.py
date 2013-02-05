'''
module to test the various subclasses of the abstract AProduct class
'''
from nose.tools import istest, eq_, raises
from jasmin_cis.test.test_files.data import *
from data_io.data_products import get_data

@istest
def get_data_accepts_valid_product():
    get_data('Cloudsat_2B_CWC_RVOD', valid_cloudsat_RVOD_file, valid_variable)

@istest
@raises(NotImplementedError)
def get_data_throws_NotImplementedError_for_missing_product():
    get_data('Cloudsat_NotYetImplemented', valid_cloudsat_RVOD_file, valid_variable)

@istest
@raises(TypeError)
def get_data_throws_TypeError_for_invalid_product():
    from data_io.data_products import AProduct
    # Create a class which subclasses AProduct but doesn't fully implement the interface
    class My_test_product(AProduct): pass
    get_data('My_test_product', valid_cloudsat_RVOD_file, valid_variable)