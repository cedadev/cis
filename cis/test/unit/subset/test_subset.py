"""
Unit tests for the top-level subsetting routines.
Note that the set_limit mocks are setup for each test using the start/stop methods in setup
 and teardown respectively, but that the constrain methods are patched out on a per-test basis, this is just
 because some tests rely on the constrain call having different side effects.
"""
from unittest import TestCase
from hamcrest import assert_that, is_
from cis.data_io.ungridded_data import UngriddedDataList
from cis.data_io.gridded_data import GriddedDataList, make_from_cube
from cis.test.util.mock import make_regular_2d_ungridded_data, make_square_5x3_2d_cube


class TestSubsetOnUngriddedData(TestCase):

    def setUp(self):
        """
        Setup the test harnesses, the various mocks and variables are set here, but some may be overriden by the
        individual tests.
        :return:
        """
        self.xmin, self.xmax = -10, 10
        self.ymin, self.ymax = 40, 60
        self.limits = {'x': [self.xmin, self.xmax],
                       'y': [self.ymin, self.ymax]}

    def test_GIVEN_single_variable_WHEN_subset_THEN_Subsetter_called_correctly(self):
            subset = make_regular_2d_ungridded_data().subset(**self.limits)

            assert_that(subset.data_flattened.tolist(),
                        is_([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_DataWriter_called_correctly(self):
        data = UngriddedDataList([make_regular_2d_ungridded_data(), make_regular_2d_ungridded_data()])

        subset = data.subset(**self.limits)
        assert_that(subset[0].data_flattened.tolist(), is_([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

    def test_GIVEN_named_variables_WHEN_subset_THEN_coordinates_found_correctly(self):
        self.limits = {'lon': [self.xmin, self.xmax],
                       'lat': [self.ymin, self.ymax]}

        data = UngriddedDataList([make_regular_2d_ungridded_data(), make_regular_2d_ungridded_data()])

        subset = data.subset(**self.limits)
        assert_that(subset[0].data_flattened.tolist(), is_([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))


class TestSubsetOnGriddedData(TestCase):

    def setUp(self):
        self.xmin, self.xmax = 0, 5
        self.ymin, self.ymax = -5, 5
        self.limits = {'x': [self.xmin, self.xmax],
                       'y': [self.ymin, self.ymax]}
        self.data = make_from_cube(make_square_5x3_2d_cube())

    def test_GIVEN_single_variable_WHEN_subset_THEN_Subsetter_called_correctly(self):

            subset = self.data.subset(**self.limits)
            assert_that(subset.data.tolist(),
                        is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_Subsetter_called_correctly(self):

        data = GriddedDataList([make_square_5x3_2d_cube(), make_square_5x3_2d_cube()])

        subset = data.subset(**self.limits)
        assert_that(subset[0].data.tolist(), is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
        assert_that(subset[1].data.tolist(), is_(subset[0].data.tolist()))

    def test_GIVEN_standard_named_variables_WHEN_subset_THEN_coordinates_found_correctly(self):
        self.limits = {'longitude': [self.xmin, self.xmax],
                       'latitude': [self.ymin, self.ymax]}

        subset = self.data.subset(**self.limits)

        assert_that(subset.data.tolist(), is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
