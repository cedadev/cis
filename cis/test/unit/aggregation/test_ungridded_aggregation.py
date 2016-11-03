from unittest import TestCase

from nose.tools import istest

from cis.data_io.gridded_data import GriddedDataList
from cis.data_io.ungridded_data import UngriddedDataList
from cis.collocation.col_implementations import mean, max, min, stddev, moments
from cis.test.utils_for_testing import *

from cis.test.util.mock import *


class TestUngriddedAggregation(TestCase):
    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_single_point_in_one_dimension(self):
        grid = {'y': slice(-12.5, 12.5, 5)}

        data = make_dummy_ungridded_data_single_point()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_can_name_variables_by_standard_name(self):
        """
        Note that this is also the variable name for many ungridded cases
        """
        grid = {'latitude': slice(-12.5, 12.5, 5)}

        data = make_dummy_ungridded_data_single_point()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_aggregating_defaults(self):
        """
        Testing default aggregation edges. Note that the upper edges of the
        ungridded data points array are removed from the aggregate because they fall on the respective cells' upper
        bounds.
        """
        grid = {'x': slice(None, 5, 5), 'y': slice(-10, None, 5)}

        data = make_regular_2d_ungridded_data()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.array([[1.0, 2.0],  # 3.0],
                              [4.0, 5.0],  # 6.0],
                              [7.0, 8.0],  # 9.0],
                              [10.0, 11.0]])  # 12.0],
        # [13.0, 14.0, 15.0]],

        assert_arrays_almost_equal(cube_out.data, result)

    @istest
    def test_aggregating_single_point_in_one_dimension_lower_bound_edge_case(self):
        """
        Test to document the behaviour of aggregation when a point on a cell's lower bound is taken to be in that cell
          or out of it. If the point is on the lower bound it is taken to be part of that cell.
        """
        grid = {'y': slice(-12.5, 12.5, 5)}

        data = make_dummy_ungridded_data_single_point(lat=-2.50000)

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_aggregating_single_point_in_one_dimension_upper_bound_edge_case(self):
        """
        Test to document the behaviour of aggregation when a point on a cell's upper bound is taken to be in that cell
          or out of it. If the point is on the upper bound it is taken to be part of that cell.
        """
        grid = {'y': slice(-12.5, 12.5, 5)}

        data = make_dummy_ungridded_data_single_point(lat=2.50000)

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[0], [0], [0.0], [1.0], [0]], mask=[[1], [1], [1], [0], [1]], fill_value=float('inf'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_aggregating_edge_cases(self):
        """
        Further tests to reinforce the above edge case tests in two dimensions. Note that the upper edges of the
        ungridded data points array are removed from the aggregate because they fall on the respective cells' upper
        bounds.
        """
        grid = {'x': slice(-5, 5, 5), 'y': slice(-10, 10, 5)}

        data = make_regular_2d_ungridded_data()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.array([[1.0, 2.0],  # 3.0],
                              [4.0, 5.0],  # 6.0],
                              [7.0, 8.0],  # 9.0],
                              [10.0, 11.0]])  # 12.0],
        # [13.0, 14.0, 15.0]],

        assert_arrays_almost_equal(cube_out.data, result)

    @istest
    def test_aggregating_simple_dataset_in_two_dimensions_with_missing_values(self):
        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 5)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_mean_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 12.5)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[2.5, 2.0, 4.5],
                                 [8.5, 11.0, 13.5]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_max_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = max()

        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 12.5)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[4.0, 2.0, 6.0],
                                 [10.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_min_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = min()

        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 12.5)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [7.0, 8.0, 12.0]],
                                mask=[[0, 0, 0],
                                      [0, 0, 0]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    @istest
    def test_stddev_kernel_with_dataset_in_two_dimensions_with_missing_values(self):
        self.kernel = stddev()

        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 12.5)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        cube_out = data.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[numpy.sqrt(4.5), float('NaN'), numpy.sqrt(4.5)],
                                 [numpy.sqrt(4.5), 3.0, numpy.sqrt(4.5)]],
                                mask=[[0, 1, 0],
                                      [0, 0, 0]], fill_value=float('nan'))

        compare_masked_arrays(cube_out.data, result)

    def test_aggregation_one_dim_using_moments_kernel(self):
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': slice(-12.5, 12.5, 12.5)}

        output = data.aggregate(how='moments', **grid)

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
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': slice(-12.5, 12.5, 15), 'x': slice(-7.5, 7.5, 10)}

        output = data.aggregate(how='moments', **grid)

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
        grid = {'x': slice(125, 270, 40)}
        output = data.aggregate(how=self.kernel, **grid)
        assert_arrays_equal(output.data, [[13.5, 5.5, 6.5, 7.5]])

    def test_aggregating_on_grid_minus_180_to_180_when_data_is_0_to_360(self):
        data = make_regular_2d_ungridded_data(lat_dim_length=2, lon_dim_length=9, lon_min=5., lon_max=325.)
        grid = {'x': slice(-75, 125, 40)}
        output = data.aggregate(how=self.kernel, **grid)
        assert_arrays_equal(output.data, [[12.5, 13.5, 5.5, 6.5, 7.5]])

    def test_collapsed_coords_get_output_as_length_1(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': slice(0, 360, 10)}
        output = data.aggregate(how=self.kernel, **grid)
        lat = output.coord('latitude')
        assert_that(lat.points, is_([0]))

    def test_collapsed_coords_get_max_min_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'y': slice(-90, 90, 10)}
        output = data.aggregate(how=self.kernel, **grid)
        lon = output.coord('longitude')
        assert_arrays_equal(lon.bounds, [[-5, 5]])

    def test_aggregating_coord_to_length_one_with_explicit_bounds_gets_output_as_length_one(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': slice(-180, 180, 360), 'y': slice(-90, 90, 10),}
        output = data.aggregate(how=self.kernel, **grid)
        lon = output.coord('longitude')
        assert_that(lon.points, is_([0]))

    def test_aggregating_to_length_one_with_explicit_bounds_get_correct_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': slice(-180, 180, 360), 'y': slice(-90, 90, 10),}
        output = data.aggregate(how=self.kernel, **grid)
        lon = output.coord('longitude')
        assert_arrays_equal(lon.bounds, [[-180, 180]])

    def test_aggregating_over_time(self):
        from datetime import datetime, timedelta
        from cis.time_util import cis_standard_time_unit as tunit
        data = make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        output = data.aggregate(t=slice(datetime(1984, 8, 1), datetime(1984, 9, 30), timedelta(days=30)))
        expected_t_bounds = [[tunit.date2num(datetime(1984, 8, 1)), tunit.date2num(datetime(1984, 8, 31))],
                             [tunit.date2num(datetime(1984, 8, 31)), tunit.date2num(datetime(1984, 9, 30))]]
        assert_arrays_equal(output[0].coord('time').bounds, expected_t_bounds)
        assert_arrays_equal(output[0].data, [[[2.5, 10]]])

    def test_aggregating_over_time_with_default_times(self):
        from datetime import datetime, timedelta
        from cis.time_util import cis_standard_time_unit as tunit
        data = make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        output = data.aggregate(t=slice(None, None, timedelta(days=30)))
        expected_t_bounds = [[tunit.date2num(datetime(1984, 8, 27)), tunit.date2num(datetime(1984, 9, 10))]]
        assert_arrays_equal(output[0].coord('time').bounds, expected_t_bounds)
        assert_arrays_equal(output[0].data, [[[7.5]]])

    def test_aggregating_over_time_with_partial_datetime(self):
        from cis.time_util import PartialDateTime, cis_standard_time_unit as tunit
        from datetime import datetime, timedelta
        data = make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        output = data.aggregate(t=[PartialDateTime(1984,9), timedelta(days=30)])
        expected_t_bounds = [[tunit.date2num(datetime(1984, 9, 1)), tunit.date2num(datetime(1984, 10, 1))]]
        assert_arrays_almost_equal(output[0].coord('time').bounds, expected_t_bounds)
        assert_arrays_almost_equal(output[0].data, [[[10.5]]])

    @raises(ValueError)
    def test_empty_step_raises_error_with_partial_datetime(self):
        from cis.time_util import PartialDateTime
        data = make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        output = data.aggregate(t=[PartialDateTime(1984, 9), None])

    @raises(ValueError)
    def test_empty_step_raises_error(self):
        data = make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        output = data.aggregate(x=slice(1, 2, None))


class TestUngriddedListAggregation(TestCase):
    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_list_of_datasets_over_two_dims(self):
        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 5)}

        datalist = UngriddedDataList([make_regular_2d_ungridded_data_with_missing_values(),
                                      make_regular_2d_ungridded_data_with_missing_values()])

        cube_out = datalist.aggregate(how=self.kernel, **grid)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('nan'))

        assert len(cube_out) == 2
        compare_masked_arrays(cube_out[0].data, result)
        compare_masked_arrays(cube_out[1].data, result)

    def test_aggregation_one_dim_using_moments_kernel(self):
        self.kernel = moments()
        data1 = make_regular_2d_ungridded_data_with_missing_values()
        data2 = make_regular_2d_ungridded_data_with_missing_values()
        data2.metadata._name = 'snow'
        data2._data += 10
        data = UngriddedDataList([data1, data2])
        grid = {'y': slice(-12.5, 12.5, 12.5)}

        output = data.aggregate(how=self.kernel, **grid)

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
        grid = {'y': slice(-12.5, 12.5, 15), 'x': slice(-7.5, 7.5, 10)}

        output = data.aggregate(how=self.kernel, **grid)

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
        grid = {'x': slice(-7.5, 7.5, 5), 'y': slice(-12.5, 12.5, 5)}

        var_0 = make_regular_2d_ungridded_data_with_missing_values()
        var_1 = make_regular_2d_ungridded_data_with_missing_values()

        var_1.data.mask = 1

        datalist = UngriddedDataList([var_0, var_1])

        cube_out = datalist.aggregate(how=self.kernel, **grid)

        result_0 = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0],
                                 [10.0, 11.0, 12.0],
                                 [13.0, 14.0, 15.0]],
                                mask=[[0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1],
                                      [0, 0, 0],
                                      [1, 0, 0]], fill_value=float('nan'))

        result_1 = numpy.ma.array([[1.0, 2.0, 3.0],
                                   [4.0, 5.0, 6.0],
                                   [7.0, 8.0, 9.0],
                                   [10.0, 11.0, 12.0],
                                   [13.0, 14.0, 15.0]],
                                  mask=[[1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1]], fill_value=float('nan'))

        print(cube_out[0].data.fill_value)
        assert len(cube_out) == 2
        compare_masked_arrays(cube_out[0].data, result_0)
        compare_masked_arrays(cube_out[1].data, result_1)
