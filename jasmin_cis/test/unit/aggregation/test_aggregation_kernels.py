import unittest
from hamcrest import is_, assert_that
import numpy

from jasmin_cis.col_framework import get_kernel
from jasmin_cis.aggregation.aggregation_grid import AggregationGrid
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.test.util import mock
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels


class TestMomentsKernel(unittest.TestCase):

    def test_GIVEN_gridded_data_WHEN_partial_collapse_THEN_calculations_correct(self):
        grid = {'y': AggregationGrid(-10, 10, 10, False)}
        cube = mock.make_mock_cube()
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        expected_means = numpy.array([[4, 5, 6], [11.5, 12.5, 13.5]])
        expected_std_dev = numpy.array([[3, 3, 3], 3 * [numpy.sqrt(4.5)]])
        expected_no = numpy.array([[3, 3, 3], [2, 2, 2]])
        assert_that(len(result), is_(3))
        assert_that(numpy.array_equal(result[0].data, expected_means))
        assert_that(numpy.array_equal(result[1].data, expected_std_dev))
        assert_that(numpy.array_equal(result[2].data, expected_no))

    def test_GIVEN_gridded_data_WHEN_partial_collapse_THEN_metadata_correct(self):
        grid = {'y': AggregationGrid(-10, 10, 10, False)}
        cube = mock.make_mock_cube()
        cube.standard_name = 'age_of_sea_ice'  # Use a CF compliant name
        cube.long_name = 'Age of sea ice'
        cube.var_name = 'age_ice'
        cube.units = 'years'
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        mean, stddev, num = result
        assert_that(mean.standard_name, is_('age_of_sea_ice'))
        assert_that(stddev.standard_name, is_(None))
        assert_that(num.standard_name, is_(None))
        assert_that(mean.long_name, is_('Age of sea ice'))
        assert_that(stddev.long_name, is_('Unbiased standard deviation of Age of sea ice'))
        assert_that(num.long_name, is_('Number of points used to calculate the mean of Age of sea ice'))
        assert_that(mean.var_name, is_('age_ice'))
        assert_that(stddev.var_name, is_('age_ice_std_dev'))
        assert_that(num.var_name, is_('age_ice_num_points'))
        assert_that(mean.units, is_('years'))
        assert_that(stddev.units, is_('years'))
        assert_that(num.units, is_(None))

    def test_GIVEN_gridded_data_WHEN_full_collapse_THEN_calculations_correct(self):
        grid = {'y': AggregationGrid(-10, 10, float('Nan'), False)}
        cube = mock.make_mock_cube()
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        expected_means = numpy.array([7, 8, 9])
        expected_std_dev = numpy.array(3 * [numpy.sqrt(22.5)])
        expected_no = numpy.array([5, 5, 5])
        assert_that(len(result), is_(3))
        assert_that(numpy.allclose(result[0].data, expected_means))
        assert_that(numpy.allclose(result[1].data, expected_std_dev))
        assert_that(numpy.array_equal(result[2].data, expected_no))

    def test_GIVEN_gridded_data_WHEN_full_collapse_THEN_metadata_correct(self):
        grid = {'y': AggregationGrid(-10, 10, float('Nan'), False)}
        cube = mock.make_mock_cube()
        cube.standard_name = 'age_of_sea_ice'  # Use a CF compliant name
        cube.long_name = 'Age of sea ice'
        cube.var_name = 'age_ice'
        cube.units = 'years'
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        mean, stddev, num = result
        assert_that(mean.standard_name, is_('age_of_sea_ice'))
        assert_that(stddev.standard_name, is_(None))
        assert_that(num.standard_name, is_(None))
        assert_that(mean.long_name, is_('Age of sea ice'))
        assert_that(stddev.long_name, is_('Unbiased standard deviation of Age of sea ice'))
        assert_that(num.long_name, is_('Number of points used to calculate the mean of Age of sea ice'))
        assert_that(mean.var_name, is_('age_ice'))
        assert_that(stddev.var_name, is_('age_ice_std_dev'))
        assert_that(num.var_name, is_('age_ice_num_points'))
        assert_that(mean.units, is_('years'))
        assert_that(stddev.units, is_('years'))
        assert_that(num.units, is_(None))

    def test_GIVEN_grid_contains_single_points_WHEN_collapse_THEN_stddev_undefined(self):
        grid = {'y': AggregationGrid(-10, 10, 1, False)}
        cube = mock.make_mock_cube()
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        assert_that(numpy.isnan(result[1].data).all())

if __name__ == '__main__':
    unittest.main()
