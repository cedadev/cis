import datetime
from nose.tools import istest
import numpy
from jasmin_cis.col_implementations import mean, max, min, stddev

from jasmin_cis.aggregation.aggregation_grid import AggregationGrid
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.test.test_util.mock import make_mock_cube, make_dummy_ungridded_data_single_point, make_regular_2d_ungridded_data_with_missing_values
from jasmin_cis.parse_datetime import date_delta_creator, parse_datetime

import iris.unit
import iris.analysis


class TestGriddedAggregation():
    def __init__(self):
        self.cube = make_mock_cube()
        self.kernel = iris.analysis.MEAN

    @istest
    def test_aggregating_to_same_grid_returns_original_data(self):
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        assert numpy.array_equal(self.cube.data, cube_out.data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_collapsing_coordinate_collapses_coordinate(self):
        grid = {'x': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_everything_returns_a_single_value(self):
        grid = {'x': AggregationGrid(-12.5, 12.5, float('NaN'), False), 'y': AggregationGrid(0, 1, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([8])

        assert numpy.array_equal(result, cube_out.data)

    @istest
    def test_aggregating_using_max_kernel_returns_maximums(self):
        self.kernel = iris.analysis.MAX
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([13, 14, 15])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_aggregating_using_min_kernel_returns_minimums(self):
        self.kernel = iris.analysis.MIN
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([1, 2, 3])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_aggregating_using_std_dev_kernel_returns_sample_standard_deviation(self):
        self.kernel = iris.analysis.STD_DEV
        grid = {'y': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([numpy.sqrt(22.5), numpy.sqrt(22.5), numpy.sqrt(22.5)])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_aggregating_using_mean_and_coarser_grid(self):
        grid = {'x': AggregationGrid(0, 0, float('NaN'), False), 'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([5, 12.5])

        assert numpy.array_equal(result, cube_out.data)

    @istest
    def test_aggregation_on_three_dimensional_grid_with_time(self):
        self.cube = make_mock_cube(time_dim_length=7)
        start_time = parse_datetime('1984-8-27', None, None)
        end_time = parse_datetime('1984-9-2', None, None)
        delta_time = date_delta_creator(0, day=2, hour=8)
        grid = {'t': AggregationGrid(start_time, end_time, delta_time, True),
                'x': AggregationGrid(0, 0, float('NaN'), False),
                'y': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result_data = numpy.array([51, 53.5, 55.5])

        units = self.cube.coords('time')[0].units

        result_coord = numpy.array([units.date2num(datetime.datetime(1984, 8, 28, 4, 0, 0)),
                                    units.date2num(datetime.datetime(1984, 8, 30, 12, 0, 0)),
                                    units.date2num(datetime.datetime(1984, 9, 1, 20, 0))])

        assert numpy.array_equal(result_data, cube_out.data)
        assert numpy.array_equal(result_coord, cube_out.coords('time')[0].points)


class TestUngriddedAggregation:
    def __init__(self):
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
    def test_aggregating_simple_dataset_in_two_dimensions_with_mising_values(self):

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

        assert numpy.array_equal(numpy.ma.filled(cube_out.data), numpy.ma.filled(result))

