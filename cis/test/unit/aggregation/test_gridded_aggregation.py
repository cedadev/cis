from unittest import TestCase

from nose.tools import istest, eq_
import iris.analysis

from cis.data_io.gridded_data import GriddedDataList
from cis.aggregation.gridded_collapsor import GriddedCollapsor
from cis.test.utils_for_testing import *
from cis.aggregation.collapse_kernels import aggregation_kernels
from cis.test.util.mock import *
from cis.data_io.gridded_data import make_from_cube


class TestGriddedCollapse(TestCase):
    def setUp(self):
        self.cube = make_from_cube(make_mock_cube())
        self.kernel = iris.analysis.MEAN

    @istest
    def test_collapsing_coordinate_collapses_coordinate(self):
        cube_out = self.cube.collapsed('x', how=self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert_arrays_almost_equal(result, cube_out[0].data)
        assert_arrays_almost_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_collapsing_coordinate_takes_start_end_but_ignores_them(self):
        cube_out = self.cube.collapsed('x', how=self.kernel)

        result = numpy.array([2, 5, 8, 11, 14])

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert_arrays_almost_equal(result, cube_out[0].data)
        assert_arrays_almost_equal(self.cube.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    @istest
    def test_can_name_variables_by_standard_name(self):
        cube_out = self.cube.collapsed(['longitude', 'latitude'], how=self.kernel)

        result = numpy.array([8.0])

        assert_arrays_almost_equal(result, cube_out[0].data)

    @istest
    def test_can_name_variables_by_variable_name(self):
        cube_out = self.cube.collapsed(['lon', 'lat'], how=self.kernel)

        result = numpy.array([8.0])

        assert_arrays_almost_equal(result, cube_out[0].data)

    @istest
    def test_collapsing_everything_returns_a_single_value(self):
        cube_out = self.cube.collapsed(['x', 'y'], how=self.kernel)

        result = numpy.array([8.0])

        assert_arrays_almost_equal(result, cube_out[0].data)

    @istest
    def test_collapsing_everything_returns_a_single_value_with_missing_values(self):
        self.cube = make_from_cube(make_5x3_lon_lat_2d_cube_with_missing_data())

        cube_out = self.cube.collapsed(['x', 'y'], how=self.kernel)

        # result = numpy.array(8.1538461538461533)
        result = numpy.array(numpy.mean(self.cube.data))

        assert numpy.allclose(result, cube_out[0].data, rtol=1e-2)

    @istest
    def test_aggregating_using_max_kernel_returns_maximums(self):
        self.kernel = iris.analysis.MAX
        cube_out = self.cube.collapsed(['x', 'y'], how=self.kernel)

        result = numpy.array(15)

        assert_arrays_almost_equal(result, cube_out[0].data)

    @istest
    def test_aggregating_using_min_kernel_returns_minimums(self):
        self.kernel = iris.analysis.MIN
        cube_out = self.cube.collapsed(['x', 'y'], how=self.kernel)

        result = numpy.array(1)

        assert_arrays_almost_equal(result, cube_out[0].data)

    @istest
    def test_aggregating_using_std_dev_kernel_returns_sample_standard_deviation(self):
        self.kernel = iris.analysis.STD_DEV
        cube_out = self.cube.collapsed(['y'], how=self.kernel)

        result = numpy.array([numpy.sqrt(22.5), numpy.sqrt(22.5), numpy.sqrt(22.5)])

        assert_arrays_almost_equal(result, cube_out[0].data)
        assert_arrays_almost_equal(self.cube.coords('longitude')[0].points, cube_out.coords('longitude')[0].points)

    @istest
    def test_aggregation_on_three_dimensional_grid_with_time(self):
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7))

        cube_out = self.cube.collapsed(['t', 'x', 'y'], how=self.kernel)

        result_data = numpy.array(53)
        assert_arrays_almost_equal(result_data, cube_out[0].data)

    def test_aggregation_over_multidimensional_coord(self):
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        cube_out = self.cube.collapsed(['t', 'x', 'y', 'air_pressure'], how=self.kernel)

        result_data = numpy.array(263)
        assert_arrays_almost_equal(cube_out[0].data, result_data)

    def test_partial_aggregation_over_multidimensional_coord(self):
        # JASCIS-126
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        cube_out = self.cube.collapsed(['t'], how=self.kernel)

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
                                    [506.0, 507.0, 508.0, 509.0, 510.0]]], dtype=float)

        multidim_coord_points = numpy.array([[300000., 1000000., 1700000.],
                                             [2400000., 3100000., 3800000.],
                                             [4500000., 5200000., 5900000.],
                                             [6600000., 7300000., 8000000.],
                                             [8700000., 9400000., 10100000.]], dtype=float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)

    def test_partial_aggregation_over_multidimensional_coord_with_multi_kernel(self):
        # JASCIS-126
        from cis.aggregation.collapse_kernels import MultiKernel, StddevKernel, CountKernel
        self.kernel = MultiKernel('moments', [iris.analysis.MEAN, StddevKernel(), CountKernel()])
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        cube_out = self.cube.collapsed(['t'], how=self.kernel)

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
                                    [506.0, 507.0, 508.0, 509.0, 510.0]]], dtype=float)

        multidim_coord_points = numpy.array([[300000., 1000000., 1700000.],
                                             [2400000., 3100000., 3800000.],
                                             [4500000., 5200000., 5900000.],
                                             [6600000., 7300000., 8000000.],
                                             [8700000., 9400000., 10100000.]], dtype=float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[1].data, np.ones(result_data.shape)*10.8012345)
        assert_arrays_almost_equal(cube_out[2].data, np.ones(result_data.shape) * 7)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)

    def test_partial_aggregation_over_more_than_one_dim_on_multidimensional_coord(self):
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        cube_out = self.cube.collapsed(['t', 'x'], how=self.kernel)

        result_data = numpy.array([[51.0, 52.0, 53.0, 54.0, 55.0],
                                   [156.0, 157.0, 158.0, 159.0, 160.0],
                                   [261.0, 262.0, 263.0, 264.0, 265.0],
                                   [366.0, 367.0, 368.0, 369.0, 370.0],
                                   [471.0, 472.0, 473.0, 474.0, 475.0]], dtype=float)

        multidim_coord_points = numpy.array([1000000.,  3100000., 5200000., 7300000., 9400000.], dtype=float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)

    def test_partial_aggregation_over_more_than_one_multidimensional_coord(self):
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5, geopotential_height=True))
        cube_out = self.cube.collapsed(['t', 'x'], how=self.kernel)

        result_data = numpy.array([[51.0, 52.0, 53.0, 54.0, 55.0],
                                   [156.0, 157.0, 158.0, 159.0, 160.0],
                                   [261.0, 262.0, 263.0, 264.0, 265.0],
                                   [366.0, 367.0, 368.0, 369.0, 370.0],
                                   [471.0, 472.0, 473.0, 474.0, 475.0]], dtype=float)

        altitude_points = result_data + 9

        surface_air_pressure_points = numpy.array([1000000., 3100000., 5200000., 7300000., 9400000.], dtype=float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, surface_air_pressure_points)
        assert_arrays_almost_equal(cube_out[0].coord('altitude').points, altitude_points)

    def test_partial_aggregation_over_multidimensional_coord_along_middle_of_cube(self):
        # JASCIS-126
        self.cube = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        cube_out = self.cube.collapsed(['x'], how=self.kernel)

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
                                    [486.0, 487.0, 488.0, 489.0, 490.0]]], dtype=float)

        multidim_coord_points = numpy.array([[700000., 800000., 900000., 1000000., 1100000., 1200000., 1300000.],
                                             [2800000., 2900000., 3000000., 3100000., 3200000., 3300000., 3400000.],
                                             [4900000., 5000000., 5100000., 5200000., 5300000., 5400000., 5500000.],
                                             [7000000., 7100000., 7200000., 7300000., 7400000., 7500000., 7600000.],
                                             [9100000., 9200000., 9300000., 9400000., 9500000., 9600000., 9700000.]],
                                            dtype=float)

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
        eq_(GriddedCollapsor._calc_new_dims([0, 1, 2], {1}), [0, 1])

        # Cube dims         [0, 1, 2, 3]
        # Coord dims        [0, 1, 2]
        # Dims to collapse         ^
        # Untouched dims    [0, 1]
        # New dims          [0, 1]
        # Local dims        [2]
        # Mirrors: test_partial_aggregation_over_multidimensional_coord
        eq_(GriddedCollapsor._calc_new_dims([0, 1, 2], {2}), [0, 1])

        # Cube dims         [0, 1, 2, 3]
        # Coord dims        [0, ., 1, 2]
        # Coord dims        [0, 2, 3]
        # Dims to collapse   ^
        # Untouched dims    [1, 2]
        # New dims          [1, 2]
        # Local dims        [0]
        # Mirrors: test_netCDF_gridded_hybrid_height_partial
        eq_(GriddedCollapsor._calc_new_dims([0, 2, 3], {0}), [1, 2])

        # Test collapsing multiple dimensions
        eq_(GriddedCollapsor._calc_new_dims([0, 1, 2], {0, 1}), [0])

        # Test collapsing multiple dimensions, some of which aren't on the coordinate
        eq_(GriddedCollapsor._calc_new_dims([0, 1, 2], {2, 3}), [0, 1])


class TestGriddedListAggregation(TestCase):
    def setUp(self):
        self.kernel = iris.analysis.MEAN

    def test_collapse_coordinate(self):
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube())
        data2 = make_from_cube(make_mock_cube(data_offset=1))
        datalist = GriddedDataList([data1, data2])
        cube_out = datalist.collapsed(['x'], how=self.kernel)

        result1 = numpy.array([2, 5, 8, 11, 14])
        result2 = result1 + 1

        assert isinstance(cube_out, GriddedDataList)

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert_arrays_almost_equal(result1, cube_out[0].data)
        assert_arrays_almost_equal(result2, cube_out[1].data)
        assert numpy.array_equal(data1.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    def test_collapse_vertical_coordinate(self):
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube(alt_dim_length=6))
        data2 = make_from_cube(make_mock_cube(alt_dim_length=6, data_offset=1))
        datalist = GriddedDataList([data1, data2])
        cube_out = datalist.collapsed(['z'], how=self.kernel)

        result1 = data1.data.mean(axis=2)
        result2 = result1 + 1

        assert isinstance(cube_out, GriddedDataList)

        # There is a small deviation to the weighting correction applied by Iris when completely collapsing
        assert_arrays_almost_equal(result1, cube_out[0].data)
        assert_arrays_almost_equal(result2, cube_out[1].data)
        assert numpy.array_equal(data1.coords('latitude')[0].points, cube_out.coords('latitude')[0].points)

    def test_collapse_vertical_coordinate_weighted_aggregator(self):
        """
        We use a weighted aggregator, though no weights should be applied since we're only summing over the vertical
        """
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube(alt_dim_length=6))
        data2 = make_from_cube(make_mock_cube(alt_dim_length=6, data_offset=1))
        datalist = GriddedDataList([data1, data2])
        cube_out = datalist.collapsed(['z'], how=iris.analysis.SUM)

        result1 = np.sum(data1.data, axis=2)
        result2 = np.sum(data2.data, axis=2)

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
        cube_out = datalist.collapsed(['y'], how=self.kernel)

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

        output = data.collapsed(['x'], how=self.kernel)

        expect_mean = numpy.array([[5.5, 8.75, 9]])
        expect_stddev = numpy.array([numpy.sqrt(15), numpy.sqrt(26.25), numpy.sqrt(30)])
        expect_count = numpy.array([[4, 4, 4]])

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, stddev_1, count_1, mean_2, stddev_2, count_2 = output
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
        output = data.collapsed(['x', 'y'], how=self.kernel)

        expect_mean = numpy.array(7.75)
        expect_stddev = numpy.array(numpy.sqrt(244.25 / 11))
        expect_count = numpy.array(12)

        assert isinstance(output, GriddedDataList)
        assert len(output) == 6
        mean_1, stddev_1, count_1, mean_2, stddev_2, count_2 = output
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

    def test_partial_aggregation_over_more_than_one_dim_on_multidimensional_coord(self):
        from cis.data_io.gridded_data import GriddedDataList, make_from_cube

        data1 = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5))
        data2 = make_from_cube(make_mock_cube(time_dim_length=7, hybrid_pr_len=5, data_offset=1))
        datalist = GriddedDataList([data1, data2])

        cube_out = datalist.collapsed(['t', 'x'], how=self.kernel)

        result_data = numpy.array([[51.0, 52.0, 53.0, 54.0, 55.0],
                                   [156.0, 157.0, 158.0, 159.0, 160.0],
                                   [261.0, 262.0, 263.0, 264.0, 265.0],
                                   [366.0, 367.0, 368.0, 369.0, 370.0],
                                   [471.0, 472.0, 473.0, 474.0, 475.0]], dtype=float)

        multidim_coord_points = numpy.array([1000000., 3100000., 5200000., 7300000., 9400000.], dtype=float)

        assert_arrays_almost_equal(cube_out[0].data, result_data)
        assert_arrays_almost_equal(cube_out[1].data, result_data+1)
        assert_arrays_almost_equal(cube_out[0].coord('surface_air_pressure').points, multidim_coord_points)
        assert_arrays_almost_equal(cube_out[1].coord('surface_air_pressure').points, multidim_coord_points)

