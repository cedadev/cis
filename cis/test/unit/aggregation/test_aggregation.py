from unittest import TestCase

from nose.tools import istest, eq_
import iris.analysis

from cis.data_io.gridded_data import make_from_cube, GriddedDataList
from cis.data_io.ungridded_data import UngriddedDataList
from cis.collocation.col_implementations import mean, max, min, stddev, moments
from cis.aggregation.aggregation_grid import AggregationGrid
from cis.aggregation.aggregator import Aggregator
from cis.test.utils_for_testing import *
from cis.aggregation.aggregation_kernels import aggregation_kernels
from cis.test.util.mock import *


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
        assert_arrays_almost_equal(result, cube_out[0].data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_coordinate_takes_start_end_but_ignores_them(self):
        grid = {'x': AggregationGrid(0, 5, float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert_arrays_almost_equal(result, cube_out[0].data)
        assert numpy.array_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_can_name_variables_by_standard_name(self):
        grid = {'longitude': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'latitude': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array(8.0)

        assert numpy.array_equal(result, cube_out[0].data)

    @istest
    def test_can_name_variables_by_variable_name(self):
        grid = {'lon': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'lat': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result = numpy.array(8.0)

        assert numpy.array_equal(result, cube_out[0].data)

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
        assert_arrays_almost_equal(result_data, cube_out[0].data)

    def test_aggregation_over_multidimensional_coord(self):
        self.cube = make_mock_cube(time_dim_length=7, hybrid_pr_len=5)
        grid = {'t': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), True),
                'x': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'y': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False),
                'air_pressure': AggregationGrid(float('Nan'), float('Nan'), float('NaN'), False)}

        agg = Aggregator(self.cube, grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result_data = numpy.array(263)
        assert_arrays_almost_equal(cube_out[0].data, result_data)

    def test_partial_aggregation_over_multidimensional_coord(self):
        from cis.data_io.gridded_data import GriddedData
        # JASCIS-126
        self.cube = make_mock_cube(time_dim_length=7, hybrid_pr_len=5)
        grid = {'t': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), True)}

        agg = Aggregator(GriddedData.make_from_cube(self.cube), grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result_data = numpy.array([[[16.0, 17.0, 18.0, 19.0, 20.0],
                                    [51.0, 52.0, 53.0, 54.0, 55.0],
                                    [86.0, 87.0, 88.0, 89.0, 90.0]],

                                   [[121.0, 122.0, 123.0, 124.0, 125.0],
                                    [156.0, 157.0, 158.0, 159.0, 160.0],
                                    [191.0, 192.0, 193.0, 194.0, 195.0]],

                                   [[226.0, 227.0, 228.0, 229.0, 230.0],
                                    [261.0, 262.0, 263.0, 264.0, 265.0],
                                    [296.0, 297.0, 298.0, 299.0, 300]],

                                   [[331.0, 332.0, 333.0, 334.0, 335.0],
                                    [366.0, 367.0, 368.0, 369.0, 370.0],
                                    [401.0, 402.0, 403.0, 404.0, 405.0]],

                                   [[436.0, 437.0, 438.0, 439.0, 440.0],
                                    [471.0, 472.0, 473.0, 474.0, 475.0],
                                    [506.0, 507.0, 508.0, 509.0, 510.0]]], dtype=np.float)

        multidim_coord_points = numpy.array([[300000., 1000000., 1700000.],
                                             [2400000., 3100000., 3800000.],
                                             [4500000., 5200000., 5900000.],
                                             [6600000., 7300000., 8000000.],
                                             [8700000., 9400000., 10100000.]], dtype=np.float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)

    def test_partial_aggregation_over_multidimensional_coord_along_middle_of_cube(self):
        from cis.data_io.gridded_data import GriddedData
        # JASCIS-126
        self.cube = make_mock_cube(time_dim_length=7, hybrid_pr_len=5)
        grid = {'x': AggregationGrid(float('Nan'), float('Nan'), float('Nan'), False)}

        agg = Aggregator(GriddedData.make_from_cube(self.cube), grid)
        cube_out = agg.aggregate_gridded(self.kernel)

        result_data = numpy.array([[[36.0, 37.0, 38.0, 39.0, 40.0],
                                    [41.0, 42.0, 43.0, 44.0, 45.0],
                                    [46.0, 47.0, 48.0, 49.0, 50.0],
                                    [51.0, 52.0, 53.0, 54.0, 55.0],
                                    [56.0, 57.0, 58.0, 59.0, 60.0],
                                    [61.0, 62.0, 63.0, 64.0, 65.0],
                                    [66.0, 67.0, 68.0, 69.0, 70.0]],

                                   [[141.0, 142.0, 143.0, 144.0, 145.0],
                                    [146.0, 147.0, 148.0, 149.0, 150.0],
                                    [151.0, 152.0, 153.0, 154.0, 155.0],
                                    [156.0, 157.0, 158.0, 159.0, 160.0],
                                    [161.0, 162.0, 163.0, 164.0, 165.0],
                                    [166.0, 167.0, 168.0, 169.0, 170.0],
                                    [171.0, 172.0, 173.0, 174.0, 175.0]],

                                   [[246.0, 247.0, 248.0, 249.0, 250.0],
                                    [251.0, 252.0, 253.0, 254.0, 255.0],
                                    [256.0, 257.0, 258.0, 259.0, 260.0],
                                    [261.0, 262.0, 263.0, 264.0, 265.0],
                                    [266.0, 267.0, 268.0, 269.0, 270.0],
                                    [271.0, 272.0, 273.0, 274.0, 275.0],
                                    [276.0, 277.0, 278.0, 279.0, 280.0]],

                                   [[351.0, 352.0, 353.0, 354.0, 355.0],
                                    [356.0, 357.0, 358.0, 359.0, 360.0],
                                    [361.0, 362.0, 363.0, 364.0, 365.0],
                                    [366.0, 367.0, 368.0, 369.0, 370.0],
                                    [371.0, 372.0, 373.0, 374.0, 375.0],
                                    [376.0, 377.0, 378.0, 379.0, 380.0],
                                    [381.0, 382.0, 383.0, 384.0, 385.0]],

                                   [[456.0, 457.0, 458.0, 459.0, 460.0],
                                    [461.0, 462.0, 463.0, 464.0, 465.0],
                                    [466.0, 467.0, 468.0, 469.0, 470.0],
                                    [471.0, 472.0, 473.0, 474.0, 475.0],
                                    [476.0, 477.0, 478.0, 479.0, 480.0],
                                    [481.0, 482.0, 483.0, 484.0, 485.0],
                                    [486.0, 487.0, 488.0, 489.0, 490.0]]], dtype=np.float)

        multidim_coord_points = numpy.array([[700000., 800000., 900000., 1000000., 1100000., 1200000., 1300000.],
                                             [2800000., 2900000., 3000000., 3100000., 3200000., 3300000., 3400000.],
                                             [4900000., 5000000., 5100000., 5200000., 5300000., 5400000., 5500000.],
                                             [7000000., 7100000., 7200000., 7300000., 7400000., 7500000., 7600000.],
                                             [9100000., 9200000., 9300000., 9400000., 9500000., 9600000., 9700000.]],
                                            dtype=np.float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)

    def test_calc_new_dims(self):
        # Cube dims         [0, 1, 2, 3]
        # Coord dims        [0, 1, 2]
        # Dims to collapse      ^
        # Untouched dims    [0, 2]
        # New dims          [0, 1]
        # Local dims        [1]
        # Mirrors: test_partial_aggregation_over_multidimensional_coord_along_middle_of_cube
        eq_(Aggregator._calc_new_dims([0, 1, 2], {1}), [0, 1])

        # Cube dims         [0, 1, 2, 3]
        # Coord dims        [0, 1, 2]
        # Dims to collapse         ^
        # Untouched dims    [0, 1]
        # New dims          [0, 1]
        # Local dims        [2]
        # Mirrors: test_partial_aggregation_over_multidimensional_coord
        eq_(Aggregator._calc_new_dims([0, 1, 2], {2}), [0, 1])

        # Cube dims         [0, 1, 2, 3]
        # Coord dims        [0, ., 1, 2]
        # Coord dims        [0, 2, 3]
        # Dims to collapse   ^
        # Untouched dims    [1, 2]
        # New dims          [1, 2]
        # Local dims        [0]
        # Mirrors: test_netCDF_gridded_hybrid_height_partial
        eq_(Aggregator._calc_new_dims([0, 2, 3], {0}), [1, 2])

        # Test collapsing multiple dimensions
        eq_(Aggregator._calc_new_dims([0, 1, 2], {0, 1}), [0])

        # Test collapsing multiple dimensions, some of which aren't on the coordinate
        eq_(Aggregator._calc_new_dims([0, 1, 2], {2, 3}), [0, 1])


class TestGriddedListAggregation(TestCase):
    def setUp(self):
        self.kernel = iris.analysis.MEAN

    def test_collapse_coordinate(self):
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

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
        assert_arrays_almost_equal(result1, cube_out[0].data)
        assert_arrays_almost_equal(result2, cube_out[1].data)
        assert numpy.array_equal(data1.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    def test_aggregate_mean(self):
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

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
        assert_arrays_almost_equal(result1, cube_out[0].data)
        assert_arrays_almost_equal(result2, cube_out[1].data)

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
        assert_arrays_almost_equal(mean_1.data, expect_mean)
        assert_arrays_almost_equal(mean_2.data, expect_mean + 10)
        assert_arrays_almost_equal(stddev_1.data, expect_stddev)
        assert_arrays_almost_equal(stddev_2.data, expect_stddev)
        assert_arrays_almost_equal(count_1.data, expect_count)
        assert_arrays_almost_equal(count_2.data, expect_count)

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
        expect_stddev = numpy.array(numpy.sqrt(244.25 / 11))
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

        result = numpy.ma.array([[0], [0], [1.0], [0], [0]], mask=[[1], [1], [0], [1], [1]], fill_value=float('inf'))

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    @istest
    def test_can_name_variables_by_standard_name(self):
        """
        Note that this is also the variable name for many ungridded cases
        """
        grid = {'latitude': AggregationGrid(-12.5, 12.5, 5, False)}

        data = make_dummy_ungridded_data_single_point()

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        agg = Aggregator(data, grid)
        cube_out = agg.aggregate_ungridded(self.kernel)

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

        assert numpy.array_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

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

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

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

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

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

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

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

        assert_arrays_equal(numpy.ma.filled(cube_out[0].data), numpy.ma.filled(result))

    def test_aggregation_one_dim_using_moments_kernel(self):
        self.kernel = moments()
        data = make_regular_2d_ungridded_data_with_missing_values()
        grid = {'y': AggregationGrid(-12.5, 12.5, 12.5, False)}

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

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

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

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
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
        assert_arrays_equal(output[0].data, [[13.5, 5.5, 6.5, 7.5]])

    def test_aggregating_on_grid_minus_180_to_180_when_data_is_0_to_360(self):
        data = make_regular_2d_ungridded_data(lat_dim_length=2, lon_dim_length=9, lon_min=5., lon_max=325.)
        grid = {'x': AggregationGrid(-75, 125, 40, False)}
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
        assert_arrays_equal(output[0].data, [[12.5, 13.5, 5.5, 6.5, 7.5]])

    def test_collapsed_coords_get_output_as_length_1(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(0, 360, 10, False)}
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
        lat = output.coord('latitude')
        assert_that(lat.points, is_([0]))

    def test_collapsed_coords_get_max_min_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'y': AggregationGrid(-90, 90, 10, False)}
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
        lon = output.coord('longitude')
        assert_arrays_equal(lon.bounds, [[-5, 5]])

    def test_aggregating_coord_to_length_one_with_explicit_bounds_gets_output_as_length_one(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(-180, 180, 360, False), 'y': AggregationGrid(-90, 90, 10, False),}
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
        lon = output.coord('longitude')
        assert_that(lon.points, is_([0]))

    def test_aggregating_to_length_one_with_explicit_bounds_get_correct_bounds(self):
        data = make_regular_2d_ungridded_data()
        grid = {'x': AggregationGrid(-180, 180, 360, False), 'y': AggregationGrid(-90, 90, 10, False),}
        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)
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

        agg = Aggregator(data, grid)
        output = agg.aggregate_ungridded(self.kernel)

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
