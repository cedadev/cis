"""
Module to test the abstract AProduct class and it's helper methods
"""
from unittest import TestCase
from hamcrest import *

from nose.tools import eq_, raises

from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.products.AProduct import get_data, __get_class as _get_class, get_coordinates
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

    @raises(ClassNotFoundError)
    def test_given_class_which_implements_file_test_as_false_WHEN_call_get_data_for_product_THEN_class_no_found_error(self):
        from jasmin_cis.data_io.products.AProduct import AProduct

        class MyTestProduct(AProduct):
            def create_data_object(self, filenames, variable):
                pass

            def create_coords(self, filenames):
               pass

            def get_file_signature(self):
                 return [r'.*\.ending']

            def get_file_type_error(self, filesname):
                return ["Not correct type"]

        get_coordinates(["file.ending"])

    def test_given_class_which_implements_file_test_as_true_WHEN_call_get_data_for_product_THEN_test_is_checked(self):
        from jasmin_cis.data_io.products.AProduct import AProduct
        global check
        check = False

        class MyTestProductTestFileTypeTrue(AProduct):
            def create_data_object(self, filenames, variable):
                pass

            def create_coords(self, filenames):
               pass

            def get_file_signature(self):
                 return [r'.*\.endingtrue']

            def get_file_type_error(self, filesname):
                global check
                check = True
                return None

        get_coordinates(["file.endingtrue"])
        assert_that(check, is_(True), "File type check was called")


    @raises(TypeError)
    def test_that_get_data_throws_TypeError_for_invalid_product(self):
        from jasmin_cis.data_io.products.AProduct import AProduct

        class MyTestProduct(AProduct):
            """A class which subclasses AProduct but doesn't fully implement the interface"""
            def get_file_signature(self):
                return []

        my_product = MyTestProduct()


    def test_that_get_product_full_name_returns_version_product_and_cis(self):
        from jasmin_cis import __version__
        from jasmin_cis.data_io.products.AProduct import get_product_full_name
        from jasmin_cis.data_io.products.products import CloudSat

        product_name = get_product_full_name([valid_cloudsat_RVOD_file])

        assert_that(product_name, contains_string('CIS'))
        assert_that(product_name, contains_string(__version__))
        assert_that(product_name, contains_string(CloudSat.__name__))

