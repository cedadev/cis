"""
Module to test the abstract AProduct class and it's helper methods
"""
from unittest import TestCase

from hamcrest import *
from nose.tools import eq_, raises

from cis.test.integration_test_data import *
from cis.data_io.products.AProduct import get_data, __get_class as _get_class, get_coordinates
from cis.exceptions import ClassNotFoundError


class TestAProduct(TestCase):

    def test_that_get_data_accepts_valid_product(self):
        _get_class(valid_cloudsat_RVOD_file, product='CloudSat')

    def test_automatic_detection_of_product_for_existing_product(self):
        product_cls = _get_class(valid_cloudsat_RVOD_file)
        eq_(product_cls.__name__, 'CloudSat')

        product_cls = _get_class(valid_caliop_l2_filename)
        eq_(product_cls.__name__, 'Caliop_L2')

    @raises(ClassNotFoundError)
    def test_that_get_class_raises_ClassNotFoundError_for_non_existing_product(self):
        product_cls = _get_class('some_file_that_does_not_match_anything')

    @raises(ClassNotFoundError)
    def test_that_get_data_raises_ClassNotFoundError_for_missing_product(self):
        get_data(valid_cloudsat_RVOD_file, [valid_cloudsat_RVOD_sdata_variable],
                 product='Product_Not_Yet_Implemented')

    @raises(ClassNotFoundError)
    def test_given_cls_which_implements_file_test_as_false_WHEN_call_get_data_for_product_THEN_cls_no_found_error(self):
        from cis.data_io.products.AProduct import AProduct

        class MyTestProduct(AProduct):
            # Ensure this doesn't get picked up as a genuine product (when running integration tests)
            priority = -1

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
        from cis.data_io.products.AProduct import AProduct
        global check
        check = False

        class MyTestProductTestFileTypeTrue(AProduct):
            # Ensure this doesn't get picked up as a genuine product (when running integration tests)
            priority = -1

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

    def test_that_get_product_full_name_returns_version_product_and_cis(self):
        from cis import __version__
        from cis.data_io.products.AProduct import get_product_full_name
        from cis.data_io.products import CloudSat

        product_name = get_product_full_name([valid_cloudsat_RVOD_file])

        assert_that(product_name, contains_string('CIS'))
        assert_that(product_name, contains_string(__version__))
        assert_that(product_name, contains_string(CloudSat.__name__))

