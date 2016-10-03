"""
Tests the cis.col.CollocateFactory class
"""
import unittest

from hamcrest import *
from cis.collocation.col_implementations import *

from cis.collocation.col import CollocatorFactory


class TestCollocateFactory(unittest.TestCase):
    def setUp(self):
        self.factory = CollocatorFactory()

    def test_GIVEN_Factory_WHEN_request_ungridded_ungridded_box_mean_with_con_options_THEN_correct_objects_returned(
            self):
        collocator, constraint, kernel = self.factory.get_collocator_instances_for_method(
            "box", "mean", {'missing_data_for_missing_sample': "false", "h_sep": "10"}, {}, False, False)
        assert_that(collocator, instance_of(GeneralUngriddedCollocator), "Collocator's class")
        assert_that(constraint, instance_of(SepConstraintKdtree), "Constraint")
        assert_that(kernel, instance_of(mean), "Kernel")
        assert_that(constraint.h_sep, is_(10), "h_sep")

    def test_GIVEN_no_collocator_WHEN_get_col_instances_for_gridded_to_gridded_THEN_defaults_to_lin(self):
        collocator, constraint, kernel = self.factory.get_collocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, True, True)
        assert_that(collocator, instance_of(GriddedCollocator))
        assert_that(constraint, is_(None))
        assert_that(kernel, instance_of(gridded_gridded_li))

    def test_GIVEN_no_collocator_WHEN_get_col_instances_for_ungridded_to_ungridded_THEN_defaults_to_box(self):
        collocator, constraint, kernel = self.factory.get_collocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, False, False)
        assert_that(collocator, instance_of(GeneralUngriddedCollocator))
        assert_that(constraint, is_(SepConstraintKdtree))
        assert_that(kernel, is_(moments))

    def test_GIVEN_no_collocator_WHEN_get_col_instances_for_ungridded_to_gridded_THEN_correct_default_returned(self):
        collocator, constraint, kernel = self.factory.get_collocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, True, False)
        assert_that(collocator, instance_of(GeneralGriddedCollocator))
        assert_that(constraint, is_(BinnedCubeCellOnlyConstraint))
        assert_that(kernel, instance_of(moments))

    def test_GIVEN_no_collocator_WHEN_get_col_instances_for_gridded_to_ungridded_THEN_correct_default_returned(self):
        collocator, constraint, kernel = self.factory.get_collocator_instances_for_method(
            None, None, {'missing_data_for_missing_sample': "false"}, {}, False, True)
        assert_that(collocator, instance_of(GriddedUngriddedCollocator))
        assert_that(constraint, is_(None))
        assert_that(kernel, is_('linear'))
