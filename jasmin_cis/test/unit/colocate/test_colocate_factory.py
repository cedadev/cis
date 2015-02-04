"""
Tests the jasmin_cis.col.ColocateFactory class
"""
import unittest
from hamcrest import *
from jasmin_cis.col_implementations import GeneralUngriddedColocator, SepConstraintKdtree, mean
from jasmin_cis.col import ColocatorFactory


class TestColocateFactory(unittest.TestCase):

    def test_GIVEN_Factory_WHEN_request_ungridded_ungridded_box_mean_with_con_options_THEN_correct_objects_returned(self):

        factory = ColocatorFactory()

        colocator, constraint, kernel = factory.get_colocator_instances_for_method(
            "box", "mean", {'missing_data_for_missing_sample': "false", "h_sep": "10"}, {}, False, False)

        assert_that(colocator, instance_of(GeneralUngriddedColocator), "Colocator's class")
        assert_that(constraint, instance_of(SepConstraintKdtree), "Constraint")
        assert_that(kernel, instance_of(mean), "Kernel")
        assert_that(constraint.h_sep, is_(10), "h_sep")
