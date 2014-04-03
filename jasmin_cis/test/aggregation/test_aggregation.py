from nose.tools import istest
import numpy

from jasmin_cis.aggregation.aggregation_grid import AggregationGrid
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.test.test_util.mock import make_mock_cube

import iris.unit
import iris.analysis


class TestGriddedAggregation():
    def __init__(self):
        pass

    @istest
    def test_aggregating_to_same_grid_returns_original_data(self):
        cube = make_mock_cube()
        kernel = iris.analysis.MEAN
        grid = {'y': AggregationGrid(-12.5, 12.5, 5, False)}

        agg = Aggregator(cube, kernel, grid)
        cube_out = agg.aggregate_gridded()

        assert numpy.array_equal(cube.data, cube_out.data)
        assert numpy.array_equal(cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)
        assert numpy.array_equal(cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_collapsing_coordinate_collapses_coordinate(self):
        cube = make_mock_cube()
        kernel = iris.analysis.MEAN
        grid = {'x': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(cube, kernel, grid)
        cube_out = agg.aggregate_gridded()

        result = numpy.array([2, 5, 8, 11, 14])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_everything_returns_a_single_value(self):
        cube = make_mock_cube()
        kernel = iris.analysis.MEAN
        grid = {'x': AggregationGrid(-12.5, 12.5, float('NaN'), False), 'y': AggregationGrid(0, 1, float('NaN'), False)}

        agg = Aggregator(cube, kernel, grid)
        cube_out = agg.aggregate_gridded()

        result = numpy.array([8])

        assert numpy.array_equal(result, cube_out.data)

    @istest
    def test_aggregating_using_max_kernel_returns_maximums(self):
        cube = make_mock_cube()
        kernel = iris.analysis.MAX
        grid = {'x': AggregationGrid(-7.5, 7.5, 5, False), 'y': AggregationGrid(0, 0, float('NaN'), False)}

        agg = Aggregator(cube, kernel, grid)
        cube_out = agg.aggregate_gridded()

        result = numpy.array([13, 14, 15])

        assert numpy.array_equal(result, cube_out.data)
        assert numpy.array_equal(cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)






