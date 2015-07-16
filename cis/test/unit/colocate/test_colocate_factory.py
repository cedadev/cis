"""
Tests the cis.col.ColocateFactory class
"""
import unittest
from hamcrest import *
from cis.col_implementations import *
from cis.col import ColocatorFactory


class TestColocateFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ColocatorFactory()

    def test_GIVEN_Factory_WHEN_request_ungridded_ungridded_box_mean_with_con_options_THEN_correct_objects_returned(self):
        colocator, constraint, kernel = self.factory.get_colocator_instances_for_method(
            "box", "mean", {'missing_data_for_missing_sample': "false", "h_sep": "10"}, {}, False, False)
        assert_that(colocator, instance_of(GeneralUngriddedColocator), "Colocator's class")
        assert_that(constraint, instance_of(SepConstraintKdtree), "Constraint")
        assert_that(kernel, instance_of(mean), "Kernel")
        assert_that(constraint.h_sep, is_(10), "h_sep")

    def test_GIVEN_no_colocator_WHEN_get_col_instances_for_gridded_to_gridded_THEN_defaults_to_lin(self):
        colocator, constraint, kernel = self.factory.get_colocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, True, True)
        assert_that(colocator, instance_of(GriddedColocator))
        assert_that(constraint, is_(None))
        assert_that(kernel, instance_of(gridded_gridded_li))

    def test_GIVEN_no_colocator_WHEN_get_col_instances_for_ungridded_to_ungridded_THEN_defaults_to_box(self):
        colocator, constraint, kernel = self.factory.get_colocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, False, False)
        assert_that(colocator, instance_of(GeneralUngriddedColocator))
        assert_that(constraint, is_(SepConstraintKdtree))
        assert_that(kernel, is_(moments))

    def test_GIVEN_no_colocator_WHEN_get_col_instances_for_ungridded_to_gridded_THEN_correct_default_returned(self):
        colocator, constraint, kernel = self.factory.get_colocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, True, False)
        assert_that(colocator, instance_of(GeneralGriddedColocator))
        assert_that(constraint, is_(BinnedCubeCellOnlyConstraint))
        assert_that(kernel, instance_of(moments))

    def test_GIVEN_no_colocator_WHEN_get_col_instances_for_gridded_to_ungridded_THEN_correct_default_returned(self):
        colocator, constraint, kernel = self.factory.get_colocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, False, True)
        assert_that(colocator, instance_of(GeneralUngriddedColocator))
        assert_that(constraint, is_(None))
        assert_that(kernel, instance_of(nn_gridded))