from unittest import TestCase
from nose.tools import istest
import numpy

from jasmin_cis.data_io.gridded_data import make_from_cube, GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.col_implementations import mean, max, min, stddev, moments
from jasmin_cis.aggregation.aggregation_grid import AggregationGrid
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.test.utils_for_testing import *
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels
from jasmin_cis.test.util.mock import *

import iris.unit
import iris.analysis


class TestGriddedAggregation(TestCase):

    def setUp(self):
        self.cube = make_mock_cube()
        self.kernel = iris.analysis.MEAN

    @istest
    @raises(NotImplementedError)
    def test_aggregating_to_same_grid_raises_NotImplementedError(self):
        # Partial collapse of gridded data not supported (see JASCIS-148).
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        assert numpy.array_equal(self.cube.data, cube_out.data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_collapsing_coordinate_collapses_coordinate(self):
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert numpy.allclose(result, cube_out[0].data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_coordinate_takes_start_end_but_ignores_them(self):
        grid = {'x': AggregationGrid(0, 5, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert numpy.allclose(result, cube_out[0].data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_everything_returns_a_single_value(self):
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array(8.0)

        assert numpy.array_equal(result, cube_out[0].data)

    @istest
    def test_collapsing_everything_returns_a_single_value_with_missing_values(self):
        self.cube = make_5x3_lon_lat_2d_cube_with_missing_data()

        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        # result = numpy.array(8.1538461538461533)
        result = numpy.array(numpy.mean(self.cube.data))

        assert numpy.allclose(result, cube_out[0].data, rtol=1e-2)

    @istest
    def test_aggregating_using_max_kernel_returns_maximums(self):
        self.kernel = iris.analysis.MAX
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array(15)

        assert numpy.array_equal(result, cube_out[0].data)

    @istest
    def test_aggregating_using_min_kernel_returns_minimums(self):
        self.kernel = iris.analysis.MIN
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array(1)

        assert numpy.array_equal(result, cube_out[0].data)

    @istest
    def test_aggregating_using_std_dev_kernel_returns_sample_standard_deviation(self):
        self.kernel = iris.analysis.STD_DEV
        grid = {'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([numpy.sqrt(22.5), numpy.sqrt(22.5), numpy.sqrt(22.5)])

        assert numpy.array_equal(result, cube_out[0].data)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_aggregation_on_three_dimensional_grid_with_time(self):
        self.cube = make_mock_cube(time_dim_length=7)
        grid = {'t': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), True),
                'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result_data = numpy.array(53)
        assert numpy.allclose(result_data, cube_out[0].data)


class TestGriddedListAggregation(TestCase):

    def setUp(self):
        self.kernel = iris.analysis.MEAN

    def test_collapse_coordinate(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube())
        data2 = make_from_cube(make_mock_cube(data_offset=1))
        datalist = GriddedDataList([data1, data2])
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(datalist, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result1 = numpy.array([2, 5, 8, 11, 14])
        result2 = result1 + 1

        assert isinstance(cube_out, GriddedDataList)

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert numpy.allclose(result1, cube_out[0].data)
        assert numpy.allclose(result2, cube_out[1].data)
        assert numpy.array_equal(data1.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    def test_aggregate_mean(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube())
        data2 = make_from_cube(make_mock_cube(data_offset=1))
        datalist = GriddedDataList([data1, data2])
        grid = {'y': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False)}

        agg = Aggregator(datalist, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result1 = numpy.array([7, 8, 9])
        result2 = result1 + 1

        assert isinstance(cube_out, GriddedDataList)

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert numpy.allclose(result1, cube_out[0].data)
        assert numpy.allclose(result2, cube_out[1].data)

    def test_complete_collapse_one_dim_using_moments_kernel(self):
        self.kernel = aggregation_kernels['moments']
        data1 = make_from_cube(make_5x3_lon_lat_2d_cube_with_missing_data())
        data1.var_name = 'var1'
        data2 = make_from_cube(make_5x3_lon_lat_2d_cube_with_missing_data())
        data2.var_name = 'var2'
        data2.data += 10
        data = GriddedDataList([data1, data2])

        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_gridded(self.kernel)

        expect_mean = numpy.array([[5.5, 8.75, 9]])
        expect_stddev = numpy.array([numpy.sqrt(15), numpy.sqrt(26.25), numpy.sqrt(30)])
        expect_count = numpy.array([[4, 4, 4]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, mean_2, stddev_1, stddev_2, count_1, count_2 = output
        assert mean_1.var_name == 'var1'
        assert stddev_1.var_name == 'var1_std_dev'
        assert count_1.var_name == 'var1_num_points'
        assert mean_2.var_name == 'var2'
        assert stddev_2.var_name == 'var2_std_dev'
        assert count_2.var_name == 'var2_num_points'
        assert numpy.allclose(mean_1.data, expect_mean)
        assert numpy.allclose(mean_2.data, expect_mean + 10)
        assert numpy.allclose(stddev_1.data, expect_stddev)
        assert numpy.allclose(stddev_2.data, expect_stddev)
        assert numpy.allclose(count_1.data, expect_count)
        assert numpy.allclose(count_2.data, expect_count)

    def test_complete_collapse_two_dims_using_moments_kernel(self):
        self.kernel = aggregation_kernels['moments']
        data1 = make_from_cube(make_5x3_lon_lat_2d_cube_with_missing_data())
        data1.var_name = 'var1'
        data2 = make_from_cube(make_5x3_lon_lat_2d_cube_with_missing_data())
        data2.var_name = 'var2'
        data2.data += 10
        data = GriddedDataList([data1, data2])
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_gridded(self.kernel)

        expect_mean = numpy.array(7.75)
        expect_stddev = numpy.array(numpy.sqrt(244.25/11))
        expect_count = numpy.array(12)

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, mean_2, stddev_1, stddev_2, count_1, count_2 = output
        assert mean_1.var_name == 'var1'
        assert stddev_1.var_name == 'var1_std_dev'
        assert count_1.var_name == 'var1_num_points'
        assert mean_2.var_name == 'var2'
        assert stddev_2.var_name == 'var2_std_dev'
        assert count_2.var_name == 'var2_num_points'
        # Latitude area weighting means these aren't quite right so increase the rtol.
        assert numpy.allclose(mean_1.data, expect_mean, 1e-3)
        assert numpy.allclose(mean_2.data, expect_mean + 10, 1e-3)
        assert numpy.allclose(stddev_1.data, expect_stddev)
        assert numpy.allclose(stddev_2.data, expect_stddev)
        assert numpy.allclose(count_1.data, expect_count)
        assert numpy.allclose(count_2.data, expect_count)


class TestUngriddedAggregation(TestCase):
    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_single_point_in_one_dimension(self):
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

        result = numpy.ma.array([0, 0, 1.0, 0, 0], mask=[1, 1, 0, 1, 1], fill_value=float('inf'))

        assert numpy.array_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    @istest
    def test_aggregating_simple_dataset_in_two_dimensions_with_missing_values(self):

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        print cube_out.data.fill_value

        assert numpy.array_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    @istest
    def test_mean_kernel_with_dataset_in_two_dimensions_with_missing_values(self):

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

        result = numpy.ma.array([[2.5, 2.0, 4.5],
                                 [8.5, 11.0, 13.5]],

                           mask=[[0, 0, 0],
                                 [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    @istest
    def test_max_kernel_with_dataset_in_two_dimensions_with_missing_values(self):

        self.kernel = max()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

        result = numpy.ma.array([[4.0, 2.0, 6.0],
                                 [10.0, 14.0, 15.0]],

                           mask=[[0, 0, 0],
                                 [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    @istest
    def test_min_kernel_with_dataset_in_two_dimensions_with_missing_values(self):

        self.kernel = min()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

        result = numpy.ma.array([[1.0, 2.0, 3.0],
                                 [7.0, 8.0, 12.0]],

                           mask=[[0, 0, 0],
                                 [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    @istest
    def test_stddev_kernel_with_dataset_in_two_dimensions_with_missing_values(self):

        self.kernel = stddev()

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        data = make_regular_2d_ungridded_data_with_missing_values()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

        result = numpy.ma.array([[numpy.sqrt(4.5), float('NaN'), numpy.sqrt(4.5)],
                                 [numpy.sqrt(4.5), 3.0, numpy.sqrt(4.5)]],

                           mask=[[0, 1, 0],
                                 [0, 0, 0]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

    def test_aggregation_one_dim_using_moments_kernel(self):
        self.kernel = moments()
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

        expect_mean = numpy.array([3.2, 11])
        expect_stddev = numpy.array([numpy.sqrt(3.7), numpy.sqrt(26/3.0)])
        expect_count = numpy.array([5, 7])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 3
        actual_mean, actual_stddev, actual_count = output
        assert actual_mean.var_name == 'rain'
        assert actual_stddev.var_name == 'rain_std_dev'
        assert actual_count.var_name == 'rain_num_points'
        assert numpy.allclose(actual_mean.data, expect_mean)
        assert numpy.allclose(actual_stddev.data, expect_stddev)
        assert numpy.allclose(actual_count.data, expect_count)

    def test_aggregation_two_dims_using_moments_kernel(self):
        self.kernel = moments()
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': AggregationGrid(-12.5, 12.5, 15, False), 'x': AggregationGrid(-7.5, 7.5, 10, False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

        expect_mean = numpy.array([[4.4, 4.5], [35.0/3, 13.5]])
        expect_stddev = numpy.array([[numpy.sqrt(9.3), numpy.sqrt(4.5)],
                                     [numpy.sqrt(13.0/3), numpy.sqrt(4.5)]])
        expect_count = numpy.array([[5, 2], [3, 2]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 3
        actual_mean, actual_stddev, actual_count = output
        assert actual_mean.var_name == 'rain'
        assert actual_stddev.var_name == 'rain_std_dev'
        assert actual_count.var_name == 'rain_num_points'
        assert numpy.allclose(actual_mean.data, expect_mean)
        assert numpy.allclose(actual_stddev.data, expect_stddev)
        assert numpy.allclose(actual_count.data, expect_count)


class TestUngriddedListAggregation(TestCase):

    def setUp(self):
        self.kernel = mean()

    @istest
    def test_aggregating_list_of_datasets_over_two_dims(self):

        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(-12.5, 12.5, 5, False)}

        datalist = UngriddedDataList([make_regular_2d_ungridded_data_with_missing_values(),
                                     make_regular_2d_ungridded_data_with_missing_values()])

        agg = Aggregator(datalist, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        print cube_out[0].data.fill_value
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

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

        expect_mean = numpy.array([3.2, 11])
        expect_stddev = numpy.array([numpy.sqrt(3.7), numpy.sqrt(26.0/3)])
        expect_count = numpy.array([5, 7])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, stddev_1, count_1, mean_2, stddev_2, count_2 = output
        assert mean_1.var_name == 'rain'
        assert stddev_1.var_name == 'rain_std_dev'
        assert count_1.var_name == 'rain_num_points'
        assert mean_2.var_name == 'snow'
        assert stddev_2.var_name == 'snow_std_dev'
        assert count_2.var_name == 'snow_num_points'
        assert numpy.allclose(mean_1.data, expect_mean)
        assert numpy.allclose(stddev_1.data, expect_stddev)
        assert numpy.allclose(count_1.data, expect_count)
        assert numpy.allclose(mean_2.data, expect_mean + 10)
        assert numpy.allclose(stddev_2.data, expect_stddev)
        assert numpy.allclose(count_2.data, expect_count)

    def test_aggregation_two_dims_using_moments_kernel(self):
        self.kernel = moments()
        data1 = make_regular_2d_ungridded_data_with_missing_values()
        data2 = make_regular_2d_ungridded_data_with_missing_values()
        data2.metadata._name = 'snow'
        data2._data += 10
        data = UngriddedDataList([data1, data2])
        grid = {'y': AggregationGrid(-12.5, 12.5, 15, False), 'x': AggregationGrid(-7.5, 7.5, 10, False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

        expect_mean = numpy.array([[4.4, 4.5], [35.0/3, 13.5]])
        expect_stddev = numpy.array([[numpy.sqrt(9.3), numpy.sqrt(4.5)],
                                     [numpy.sqrt(13.0/3), numpy.sqrt(4.5)]])
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
        assert numpy.allclose(mean_1.data, expect_mean)
        assert numpy.allclose(stddev_1.data, expect_stddev)
        assert numpy.allclose(count_1.data, expect_count)
        assert numpy.allclose(mean_2.data, expect_mean + 10)
        assert numpy.allclose(stddev_2.data, expect_stddev)
        assert numpy.allclose(count_2.data, expect_count)