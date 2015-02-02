import unittest
from hamcrest import is_, assert_that
import numpy

from jasmin_cis.col_framework import get_kernel
from jasmin_cis.aggregation.aggregation_grid import AggregationGrid
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.test.util import mock
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels, CountKernel
from jasmin_cis.test.utils_for_testing import *


class TestMomentsKernel(unittest.TestCase):

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
        assert_that(stddev.long_name, is_('Corrected sample standard deviation of Age of sea ice'))
        assert_that(num.long_name, is_('Number of points used to calculate the mean of Age of sea ice'))
        assert_that(mean.var_name, is_('age_ice'))
        assert_that(stddev.var_name, is_('age_ice_std_dev'))
        assert_that(num.var_name, is_('age_ice_num_points'))
        assert_that(mean.units, is_('years'))
        assert_that(stddev.units, is_('years'))
        assert_that(num.units, is_(None))

    def test_GIVEN_grid_contains_single_points_WHEN_collapse_THEN_stddev_undefined(self):
        grid = {'y': AggregationGrid(-10, 10, float('Nan'), False)}
        cube = mock.make_mock_cube(2, 2)
        cube.data = numpy.ma.masked_invalid([[float('Nan'), 1], [float('Nan'), float('Nan')]])
        kernel = aggregation_kernels['moments']
        agg = Aggregator(cube, grid)
        result = agg.aggregate_gridded(kernel)

        assert_that(result[1].data.mask.all())

    def test_GIVEN_ungridded_data_WHEN_collapse_THEN_calculations_correct(self):
        grid = {'y': AggregationGrid(-12.5, 12.5, 12.5, False)}
        data = mock.make_regular_2d_ungridded_data()
        kernel_class = get_kernel('moments')
        kernel = kernel_class()
        agg = Aggregator(data, grid)
        result = agg.aggregate_ungridded(kernel)

        expected_means = numpy.array([3.5, 11])
        expected_std_dev = numpy.array([numpy.sqrt(3.5), numpy.sqrt(7.5)])
        expected_no = numpy.array([6, 9])
        assert_that(len(result), is_(3))
        assert_arrays_almost_equal(result[0].data, expected_means)
        assert_arrays_almost_equal(result[1].data, expected_std_dev)
        assert_that(numpy.array_equal(result[2].data, expected_no))

    def test_GIVEN_ungridded_data_WHEN_collapse_THEN_metadata_correct(self):
        grid = {'y': AggregationGrid(-10, 10, 10, False)}
        data = mock.make_regular_2d_ungridded_data()
        kernel_class = get_kernel('moments')
        kernel = kernel_class()
        agg = Aggregator(data, grid)
        result = agg.aggregate_ungridded(kernel)

        mean, stddev, num = result
        assert_that(mean.standard_name, is_('rainfall_rate'))
        assert_that(stddev.standard_name, is_(None))
        assert_that(num.standard_name, is_(None))
        assert_that(mean.long_name, is_('TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(stddev.long_name, is_('Corrected sample standard deviation of TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(num.long_name, is_('Number of points used to calculate the mean of '
                                       'TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(mean.var_name, is_('rain'))
        assert_that(stddev.var_name, is_('rain_std_dev'))
        assert_that(num.var_name, is_('rain_num_points'))
        assert_that(mean.units, is_('kg m-2 s-1'))
        assert_that(stddev.units, is_('kg m-2 s-1'))
        assert_that(num.units, is_(None))


class TestCountKernel(unittest.TestCase):

    def test_GIVEN_missing_data_WHEN_count_THEN_calculation_correct(self):
        cube = mock.make_5x3_lon_lat_2d_cube_with_missing_data()
        kernel = CountKernel()
        data = kernel.count_kernel_func(cube.data, 0)
        assert_that(numpy.array_equal(data, numpy.array([4, 4, 4])))

if __name__ == '__main__':
    unittest.main()
