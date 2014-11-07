"""
Module to test the abstract AProduct class and it's helper methods
"""
from unittest import TestCase

from nose.tools import eq_, raises

from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.products.AProduct import get_data, __get_class as _get_class
from jasmin_cis.exceptions import ClassNotFoundError


class TestAProduct(TestCase):

    def test_that_get_data_accepts_valid_product(self):
        _get_class(valid_cloudsat_RVOD_file, product='CloudSat')

    def test_automatic_detection_of_product_for_existing_product(self):
        product_cls = _get_class(valid_cloudsat_RVOD_file)
        eq_(product_cls.__name__, 'CloudSat')

        product_cls = _get_class(valid_caliop_l2_filename)
        eq_(product_cls.__name__, 'Caliop_L2')

    def test_GIVEN_filename_matches_cis_and_aerosol_cci_WHEN_get_class_THEN_cis_product_returned(self):
        # If a filename matches the file signature for CIS and aerosol CCI (e.g. because you subsetted
        # an Aerosol CCI product, CIS needs to identify that the CIS product takes priority
        filename = 'cis-aatsr_20100717003203-ESACCI-L2P_NEWAEROSOL-ALL-ATSR2_ERS2-ORAC_43800-fv02.02b_v1.0_odaer550.nc'
        product_cls = _get_class(filename)
        eq_(product_cls.__name__, 'cis')

    @raises(ClassNotFoundError)
    def test_that_get_class_raises_ClassNotFoundError_for_non_existing_product(self):
        product_cls = _get_class('some_file_that_does_not_match_anything')

    @raises(ClassNotFoundError)
    def test_that_get_data_raises_ClassNotFoundError_for_missing_product(self):
        get_data(valid_cloudsat_RVOD_file, [valid_cloudsat_RVOD_sdata_variable],
                 product='Product_Not_Yet_Implemented')

    @raises(TypeError)
    def test_that_get_data_throws_TypeError_for_invalid_product(self):
        from jasmin_cis.data_io.products.AProduct import AProduct

        class MyTestProduct(AProduct):
            """A class which subclasses AProduct but doesn't fully implement the interface"""
            pass
        my_product = MyTestProduct()
