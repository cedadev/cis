from unittest import TestCase

from nose.tools import istest, eq_
import iris.analysis

from cis.data_io.gridded_data import make_from_cube, GriddedDataList
from cis.data_io.ungridded_data import UngriddedDataList
from cis.collocation.col_implementations import mean, max, min, stddev, moments
from cis.aggregation.aggregation_grid import AggregationGrid
from cis.aggregation.ungridded_aggregator import UngriddedAggregator
from cis.test.utils_for_testing import *

from cis.test.util.mock import *


class TestUngriddedAggregation(TestCase):
    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_single_point_in_one_dimension(self):
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_can_name_variables_by_standard_name(self):
        """
        Note that this is also the variable name for many ungridded cases
        """
        grid = {'latitude': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_aggregating_single_point_in_one_dimension_lower_bound_edge_case(self):
        """
        Test to document the behaviour of aggregation when a point on a cell's lower bound is taken to be in that cell
          or out of it. If the point is on the lower bound it is taken to be part of that cell.
        """
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point(lat=-2.50000)

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_aggregating_single_point_in_one_dimension_upper_bound_edge_case(self):
        """
        Test to document the behaviour of aggregation when a point on a cell's upper bound is taken to be in that cell
          or out of it. If the point is on the upper bound it is NOT taken to be part of that cell.
        """
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point(lat=2.50000)

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[0], [0], [0.0], [1.0], [0]], mask=[[1], [1], [1], [0], [1]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_aggregating_edge_cases(self):
        """
        Further tests to reinforce the above edge case tests in two dimensions. Note that the upper edges of the
        ungridded data points array are removed from the aggregate because they fall on the respective cells' upper
        bounds.
        """
        grid = {'x': AggregationGrid(-5, 5, 5, False), 'y': AggregationGrid(-10, 10, 5, False)}

        data = make_regular_2d_ungridded_data()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.array([[1.0, 2.0],  # 3.0],
                              [4.0, 5.0],  # 6.0],
                              [7.0, 8.0],  # 9.0],
                              [10.0, 11.0]])  # 12.0],
        # [13.0, 14.0, 15.0]],

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_aggregating_simple_dataset_in_two_dimensions_with_missing_values(self):
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('inf'))

        assert numpy.array_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_mean_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[2.5, 2.0, 4.5],
                                 [8.5, 11.0, 13.5]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_max_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = max()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[4.0, 2.0, 6.0],
                                 [10.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_min_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = min()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [7.0, 8.0, 12.0]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_stddev_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = stddev()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = UngriddedAggregator(data, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[numpy.sqrt(4.5), float('NaN'), numpy.sqrt(4.5)],
                                 [numpy.sqrt(4.5), 3.0, numpy.sqrt(4.5)]],
                                mask=[[0, 1, 0],
                                      [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    def test_aggregation_one_dim_using_moments_kernel(self):
        self.kernel = moments()
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)

        expect_mean = numpy.array([[3.2], [11]])
        expect_stddev = numpy.array([[numpy.sqrt(3.7)], [numpy.sqrt(26 / 3.0)]])
        expect_count = numpy.array([[5], [7]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 3
        actual_mean, actual_stddev, actual_count = output
        assert actual_mean.var_name == 'rain'
        assert actual_stddev.var_name == 'rain_std_dev'
        assert actual_count.var_name == 'rain_num_points'
        assert_arrays_almost_equal(actual_mean.data, expect_mean)
        assert_arrays_almost_equal(actual_stddev.data, expect_stddev)
        assert_arrays_almost_equal(actual_count.data, expect_count)

    def test_aggregation_two_dims_using_moments_kernel(self):
        self.kernel = moments()
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': AggregationGrid(-12.5, 12.5, 15, False), 'x': AggregationGrid(-7.5, 7.5, 10, False)}

        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)

        expect_mean = numpy.array([[4.4, 4.5], [35.0 / 3, 13.5]])
        expect_stddev = numpy.array([[numpy.sqrt(9.3), numpy.sqrt(4.5)],
                                     [numpy.sqrt(13.0 / 3), numpy.sqrt(4.5)]])
        expect_count = numpy.array([[5, 2], [3, 2]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 3
        actual_mean, actual_stddev, actual_count = output
        assert actual_mean.var_name == 'rain'
        assert actual_stddev.var_name == 'rain_std_dev'
        assert actual_count.var_name == 'rain_num_points'
        assert_arrays_almost_equal(actual_mean.data, expect_mean)
        assert_arrays_almost_equal(actual_stddev.data, expect_stddev)
        assert_arrays_almost_equal(actual_count.data, expect_count)

    def test_aggregating_on_grid_0_to_360_when_data_is_minus_180_to_180(self):
        data = make_regular_2d_ungridded_data(lat_dim_length=2, lon_dim_length=9, lon_min=-175., lon_max=145.)
        grid = {'x': AggregationGrid(125, 270, 40, False)}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        assert_arrays_equal(output[0].data, [[13.5, 5.5, 6.5, 7.5]])

    def test_aggregating_on_grid_minus_180_to_180_when_data_is_0_to_360(self):
        data = make_regular_2d_ungridded_data(lat_dim_length=2, lon_dim_length=9, lon_min=5., lon_max=325.)
        grid = {'x': AggregationGrid(-75, 125, 40, False)}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        assert_arrays_equal(output[0].data, [[12.5, 13.5, 5.5, 6.5, 7.5]])

    def test_collapsed_coords_get_output_as_length_1(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(0, 360, 10, False)}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        lat = output.coord('latitude')
        assert_that(lat.points, is_([0]))

    def test_collapsed_coords_get_max_min_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'y': AggregationGrid(-90, 90, 10, False)}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        lon = output.coord('longitude')
        assert_arrays_equal(lon.bounds, [[-5, 5]])

    def test_aggregating_coord_to_length_one_with_explicit_bounds_gets_output_as_length_one(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(-180, 180, 360, False), 'y': AggregationGrid(-90, 90, 10, False),}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        lon = output.coord('longitude')
        assert_that(lon.points, is_([0]))

    def test_aggregating_to_length_one_with_explicit_bounds_get_correct_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(-180, 180, 360, False), 'y': AggregationGrid(-90, 90, 10, False),}
        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)
        lon = output.coord('longitude')
        assert_arrays_equal(lon.bounds, [[-180, 180]])


class TestUngriddedListAggregation(TestCase):
    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_list_of_datasets_over_two_dims(self):
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 5, False)}

        datalist = UngriddedDataList([make_regular_2d_ungridded_data_with_missing_values(),
                                      make_regular_2d_ungridded_data_with_missing_values()])

        agg = UngriddedAggregator(datalist, grid)
        cube_out = agg.aggregate(self.kernel)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('inf'))

        print(cube_out[0].data.fill_value)
        assert len(cube_out) == 2
        assert numpy.array_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))
        assert numpy.array_equal(numpy.ma.filled(cube_out[1].data), numpy.ma.filled(result))

    def test_aggregation_one_dim_using_moments_kernel(self):
        self.kernel = moments()
        data1 = make_regular_2d_ungridded_data_with_missing_values()
        data2 = make_regular_2d_ungridded_data_with_missing_values()
        data2.metadata._name = 'snow'
        data2._data += 10
        data = UngriddedDataList([data1, data2])
        grid = {'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)

        expect_mean = numpy.array([[3.2], [11]])
        expect_stddev = numpy.array([[numpy.sqrt(3.7)], [numpy.sqrt(26.0 / 3)]])
        expect_count = numpy.array([[5], [7]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, stddev_1, count_1, mean_2, stddev_2, count_2 = output
        assert mean_1.var_name == 'rain'
        assert stddev_1.var_name == 'rain_std_dev'
        assert count_1.var_name == 'rain_num_points'
        assert mean_2.var_name == 'snow'
        assert stddev_2.var_name == 'snow_std_dev'
        assert count_2.var_name == 'snow_num_points'
        assert_arrays_almost_equal(mean_1.data, expect_mean)
        assert_arrays_almost_equal(stddev_1.data, expect_stddev)
        assert_arrays_almost_equal(count_1.data, expect_count)
        assert_arrays_almost_equal(mean_2.data, expect_mean + 10)
        assert_arrays_almost_equal(stddev_2.data, expect_stddev)
        assert_arrays_almost_equal(count_2.data, expect_count)

    def test_aggregation_two_dims_using_moments_kernel(self):
        self.kernel = moments()
        data1 = make_regular_2d_ungridded_data_with_missing_values()
        data2 = make_regular_2d_ungridded_data_with_missing_values()
        data2.metadata._name = 'snow'
        data2._data += 10
        data = UngriddedDataList([data1, data2])
        grid = {'y': AggregationGrid(-12.5, 12.5, 15, False), 'x': AggregationGrid(-7.5, 7.5, 10, False)}

        agg = UngriddedAggregator(data, grid)
        output = agg.aggregate(self.kernel)

        expect_mean = numpy.array([[4.4, 4.5], [35.0 / 3, 13.5]])
        expect_stddev = numpy.array([[numpy.sqrt(9.3), numpy.sqrt(4.5)],
                                     [numpy.sqrt(13.0 / 3), numpy.sqrt(4.5)]])
        expect_count = numpy.array([[5, 2], [3, 2]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, stddev_1, count_1, mean_2, stddev_2, count_2 = output
        assert mean_1.var_name == 'rain'
        assert stddev_1.var_name == 'rain_std_dev'
        assert count_1.var_name == 'rain_num_points'
        assert mean_2.var_name == 'snow'
        assert stddev_2.var_name == 'snow_std_dev'
        assert count_2.var_name == 'snow_num_points'
        assert_arrays_almost_equal(mean_1.data, expect_mean)
        assert_arrays_almost_equal(stddev_1.data, expect_stddev)
        assert_arrays_almost_equal(count_1.data, expect_count)
        assert_arrays_almost_equal(mean_2.data, expect_mean + 10)
        assert_arrays_almost_equal(stddev_2.data, expect_stddev)
        assert_arrays_almost_equal(count_2.data, expect_count)

    @istest
    def test_aggregating_list_of_datasets_over_two_dims_with_diff_masks(self):
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 5, False)}

        var_0 = make_regular_2d_ungridded_data_with_missing_values()
        var_1 = make_regular_2d_ungridded_data_with_missing_values()

        var_1.data.mask = 1

        datalist = UngriddedDataList([var_1, var_0])

        agg = UngriddedAggregator(datalist, grid)
        cube_out = agg.aggregate(self.kernel)

        result_0 = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('inf'))

        result_1 = numpy.ma.array([[1.0, 2.0, 3.0],
                                   [4.0, 5.0, 6.0],
                                   [7.0, 8.0, 9.0],
                                   [10.0, 11.0, 12.0],
                                   [13.0, 14.0, 15.0]],
                                  mask=[[1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1]], fill_value=float('inf'))

        print(cube_out[0].data.fill_value)
        assert len(cube_out) == 2
        assert numpy.array_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result_1))
        assert numpy.array_equal(numpy.ma.filled(cube_out[1].data), numpy.ma.filled(result_0))
