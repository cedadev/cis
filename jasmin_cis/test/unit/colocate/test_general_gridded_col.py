import unittest
import datetime
from hamcrest import *
import numpy

from jasmin_cis.exceptions import UserPrintableException
from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.col_implementations import GeneralGriddedColocator, mean, CubeCellConstraint, \
    BinningCubeCellConstraint, moments, BinnedCubeCellOnlyConstraint
from jasmin_cis.test.util.mock import make_mock_cube, make_dummy_ungridded_data_single_point, \
    make_dummy_ungridded_data_two_points_with_different_values, make_dummy_1d_ungridded_data, \
    make_dummy_1d_ungridded_data_with_invalid_standard_name, make_square_5x3_2d_cube_with_time, \
    make_square_5x3_2d_cube_with_altitude, make_square_5x3_2d_cube_with_pressure, \
    make_square_5x3_2d_cube_with_decreasing_latitude, make_square_5x3_2d_cube, make_regular_2d_ungridded_data, \
    make_square_NxM_2d_cube_with_time, make_square_5x3_2d_cube_with_extra_dim, \
    make_regular_2d_ungridded_data_with_missing_values
from jasmin_cis.test.utils_for_testing import assert_arrays_equal, assert_arrays_almost_equal


class FastMean(object):
    return_size = 1

    def __init__(self):
        self.mean = mean()

    def get_value_for_data_only(self, data):
        return self.mean.get_value_for_data_only(data)

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        return self.mean.get_variable_details(var_name, var_long_name, var_standard_name, var_units)


class SlowMean(object):
    return_size = 1

    def __init__(self):
        self.mean = mean()

    def get_value(self, point, data):
        return self.mean.get_value(point, data)

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        return self.mean.get_variable_details(var_name, var_long_name, var_standard_name, var_units)


class FastMoments(object):
    return_size = 3

    def __init__(self):
        self.moments = moments()

    def get_value_for_data_only(self, data):
        return self.moments.get_value_for_data_only(data)

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        return self.moments.get_variable_details(var_name, var_long_name, var_standard_name, var_units)


class SlowMoments(object):
    return_size = 3

    def __init__(self):
        self.moments = moments()

    def get_value(self, point, data):
        return self.moments.get_value(point, data)

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        return self.moments.get_variable_details(var_name, var_long_name, var_standard_name, var_units)


def single_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, mask=True)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_true(con, kernel):

    mask = [[False, False, False],
            [False, False, False],
            [False, True, False],
            [False, False, False],
            [False, False, False]]
    sample_cube = make_mock_cube(mask=mask)
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9, missing_data_for_missing_sample=True)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_false(con, kernel):

    mask = [[False, False, False],
            [False, False, False],
            [False, True, False],
            [False, False, False],
            [False, False, False]]
    sample_cube = make_mock_cube(mask=mask)
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9, missing_data_for_missing_sample=False)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point([0.5, 99], [0.5, 99], [1.2, 5])
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def multiple_points_inside_grid_and_outside(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point([0.5, 99, 0.6, 3.0, -9], [0.5, 99, 0.6, 0.5, -3], [1.2, 5, 3.4, 5, 8])
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[8, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 2.3,  -999.9],
                                   [-999.9, 5, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def two_points_in_a_cell_results_in_mean_value_in_cell(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_two_points_with_different_values(0.5, 0.5, 1.2, 1.4)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.3, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def point_on_a_lat_boundary_appears_in_higher_cell(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 0.0, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def point_on_highest_lat_boundary_is_excluded(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(12.5, 0.0, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def point_on_180_is_included_in_lower_bound(con, kernel):
    sample_cube = make_square_NxM_2d_cube_with_time(start_lon=-135, end_lon=135, lon_point_count=4)
    data_point = make_dummy_ungridded_data_single_point(0, 180.0, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9, -999.9],
                                   [1.2, -999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def point_on_a_lon_boundary_appears_in_higher_cell(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.0, 2.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def point_on_a_lat_lon_boundary_appears_in_highest_cell(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 2.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_almost_equal(out_cube.data.filled(), expected_result)


def single_point_outside_grid_is_excluded(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(99, 99, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_on_grid_corner_is_counted_once(con, kernel):
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(10, 5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(con, kernel):
    sample_cube = make_square_5x3_2d_cube_with_time()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time_and_mising_samples_THEN_error(con, kernel):
    sample_cube = make_square_5x3_2d_cube_with_time()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    col = GeneralGriddedColocator(fill_value=-999.9, missing_data_for_missing_sample=True)
    assert_that(calling(col.colocate).with_args(points=sample_cube, data=data_point, constraint=con, kernel=kernel),
        raises(UserPrintableException, pattern=".*sample variable.*"))


def single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(con, kernel):
    sample_cube = make_square_5x3_2d_cube_with_time()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0))
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude(con, kernel):
        sample_cube = make_square_5x3_2d_cube_with_extra_dim()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, altitude=18)
        print sample_cube.data
        col = GeneralGriddedColocator(fill_value=-999.9)
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
        assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(con, kernel):
        sample_cube = make_square_5x3_2d_cube_with_altitude()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
        print sample_cube.data
        col = GeneralGriddedColocator(fill_value=-999.9)
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
        assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(con, kernel):
        sample_cube = make_square_5x3_2d_cube_with_altitude()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, altitude=1.0)
        col = GeneralGriddedColocator(fill_value=-999.9)
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
        expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
        assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(con, kernel):
        sample_cube = make_square_5x3_2d_cube_with_pressure()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
        print sample_cube.data
        col = GeneralGriddedColocator(fill_value=-999.9)
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
        assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(con, kernel):
    sample_cube = make_square_5x3_2d_cube_with_pressure()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, pressure=1.0)
    col = GeneralGriddedColocator(fill_value=-999.9)
    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
    expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],

                                   [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                    [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
    print out_cube.data.filled()
    assert_arrays_equal(out_cube.data.filled(), expected_result)


def can_colocate_list_of_data(constraint, kernel):
    col = GeneralGriddedColocator()
    sample = make_square_5x3_2d_cube()
    data1 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5, 0)
    data2 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5, 10)
    output = col.colocate(sample, UngriddedDataList([data1, data2]), constraint, kernel)
    assert len(output) == 2
    expected_data2 = numpy.array([[14.5, 16.5, 18.5],
                                  [26.5, 28.5, 30.5],
                                  [38.5, 40.5, 42.5],
                                  [50.5, 52.5, 54.5],
                                  [62.5, 64.5, 66.5]])
    expected_data1 = expected_data2 - 10
    assert_arrays_equal(output[0].data, expected_data1)
    assert_arrays_equal(output[1].data, expected_data2)


def single_point_results_in_single_value_in_cell_with_decreasing_latitude(con, kernel):
        sample_cube = make_square_5x3_2d_cube_with_decreasing_latitude()
        data_point = make_dummy_ungridded_data_single_point(3.0, 0.5, 1.2)
        col = GeneralGriddedColocator(fill_value=-999.9)
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=kernel)[0]
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])

        assert_arrays_equal(out_cube.data.filled(), expected_result)


def single_moments(constraint, kernel):
        col = GeneralGriddedColocator()
        sample = make_square_5x3_2d_cube()
        data = make_regular_2d_ungridded_data(10, -9.9, 9.9, 6, -4.9, 4.9, 10)
        output = col.colocate(sample, data, constraint, kernel)
        expected_data = numpy.array([[14.5, 16.5, 18.5],
                                     [26.5, 28.5, 30.5],
                                     [38.5, 40.5, 42.5],
                                     [50.5, 52.5, 54.5],
                                     [62.5, 64.5, 66.5]])
        expected_stddev = numpy.ones((5, 3)) * 3.5118845842842465
        expected_num = numpy.ones((5, 3)) * 4
        assert len(output) == 3
        assert isinstance(output, GriddedDataList)
        assert output[0].var_name == 'rain'
        assert output[1].var_name == 'rain_std_dev'
        assert output[2].var_name == 'rain_num_points'
        assert_arrays_equal(output[0].data, expected_data)
        assert numpy.allclose(output[1].data, expected_stddev)
        assert numpy.array_equal(output[2].data, expected_num)


def list_moments(constraint, kernel):
    col = GeneralGriddedColocator()
    sample = make_square_5x3_2d_cube()
    data1 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5)
    data2 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5)
    data2.metadata._name = 'snow'
    data2.data *= 2
    output = col.colocate(sample, UngriddedDataList([data1, data2]), constraint, kernel)
    assert len(output) == 6
    assert output[0].var_name == 'rain'
    assert output[1].var_name == 'rain_std_dev'
    assert output[2].var_name == 'rain_num_points'
    assert output[3].var_name == 'snow'
    assert output[4].var_name == 'snow_std_dev'
    assert output[5].var_name == 'snow_num_points'
    expected_data1 = numpy.array([[4.5, 6.5, 8.5],
                                  [16.5, 18.5, 20.5],
                                  [28.5, 30.5, 32.5],
                                  [40.5, 42.5, 44.5],
                                  [52.5, 54.5, 56.5]])
    expected_data2 = 2 * expected_data1
    expected_stddev1 = numpy.ones((5, 3)) * 3.5118845842842465
    expected_stddev2 = expected_stddev1 * 2
    expected_num = numpy.ones((5, 3)) * 4
    assert numpy.array_equal(output[0].data, expected_data1)
    assert numpy.allclose(output[1].data, expected_stddev1)
    assert numpy.array_equal(output[2].data, expected_num)
    assert numpy.array_equal(output[3].data, expected_data2)
    assert numpy.allclose(output[4].data, expected_stddev2)
    assert numpy.array_equal(output[5].data, expected_num)


class TestGeneralGriddedColocator(unittest.TestCase):

    def test_fill_value_for_cube_cell_constraint(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=SlowMean())[0]

        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)

    def test_fill_value_for_cube_cell_constraint_default_fill_value(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)
    
        col = GeneralGriddedColocator()
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=SlowMean())[0]
    
        expected_result = numpy.array([[float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
        
    def test_single_point_results_in_single_value_in_cell(self):
        con = CubeCellConstraint()
        kernel = SlowMean()
        single_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_cell_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        single_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_cell_using_binned_cells_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_cell_using_binned_cells_only_and_fast_kernel(self):

        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()
        single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_masked_point_results_in_single_value_in_cell_using_kernel_and_con_binned(self):
        from jasmin_cis.col_implementations import max
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_true(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_masked_cell_using_fast_kernel_and_con_missing_for_masked_true(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        single_masked_point_results_in_single_value_in_cell_using_kernel_and_con(con, kernel)

    def test_single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_true_binned_only(self):
        from jasmin_cis.col_implementations import max
        con = BinnedCubeCellOnlyConstraint()
        kernel = max()

        single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_true(con, kernel)

    def test_single_point_results_in_single_value_in_masked_cell_using_fast_kernel_and_con_missing_for_masked_true_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_masked_cell_using_kernel_and_con_missing_for_masked_true(con, kernel)

    def test_two_points_in_a_cell_results_in_mean_value_in_cell(self):
        con = CubeCellConstraint()
        kernel = SlowMean()
        two_points_in_a_cell_results_in_mean_value_in_cell(con, kernel)

    def test_two_points_in_a_cell_results_in_mean_value_in_cell_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        two_points_in_a_cell_results_in_mean_value_in_cell(con, kernel)

    def test_two_points_in_a_cell_results_in_mean_value_in_cell_using_binned_cells_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()
        two_points_in_a_cell_results_in_mean_value_in_cell(con, kernel)

    def test_two_points_in_a_cell_results_in_fast_mean_value_in_cell_using_binned_cells_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()
        two_points_in_a_cell_results_in_mean_value_in_cell(con, kernel)

    def test_point_on_a_lat_boundary_appears_in_higher_cell(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        point_on_a_lat_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lat_boundary_appears_in_higher_cell_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        point_on_a_lat_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lat_boundary_appears_in_higher_cell_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        point_on_a_lat_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lat_boundary_appears_in_higher_cell_using_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        point_on_a_lat_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_highest_lat_boundary_is_excluded(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        point_on_highest_lat_boundary_is_excluded(con, kernel)

    def test_point_on_highest_lat_boundary_is_excluded_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        point_on_highest_lat_boundary_is_excluded(con, kernel)

    def test_point_on_highest_lat_boundary_is_excluded_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        point_on_highest_lat_boundary_is_excluded(con, kernel)

    def test_point_on_highest_lat_boundary_is_excluded_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        point_on_highest_lat_boundary_is_excluded(con, kernel)

    def test_point_on_180_is_included_in_lower_bound_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        point_on_180_is_included_in_lower_bound(con, kernel)

    def test_point_on_180_is_included_in_lower_bound_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        point_on_180_is_included_in_lower_bound(con, kernel)

    def test_point_on_a_lon_boundary_appears_in_higher_cell(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        point_on_a_lon_boundary_appears_in_higher_cell(con, kernel)
    
    def test_point_on_a_lon_boundary_appears_in_higher_cell_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        point_on_a_lon_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lon_boundary_appears_in_higher_cell_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()
        point_on_a_lon_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lon_boundary_appears_in_higher_cell_using_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()
        point_on_a_lon_boundary_appears_in_higher_cell(con, kernel)

    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell(self):
        con = CubeCellConstraint()

        kernel = SlowMean()

        point_on_a_lat_lon_boundary_appears_in_highest_cell(con, kernel)
    
    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        point_on_a_lat_lon_boundary_appears_in_highest_cell(con, kernel)

    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        point_on_a_lat_lon_boundary_appears_in_highest_cell(con, kernel)

    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell_using_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        point_on_a_lat_lon_boundary_appears_in_highest_cell(con, kernel)

    def test_single_point_outside_grid_is_excluded(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        single_point_outside_grid_is_excluded(con, kernel)
    
    def test_single_point_outside_grid_is_excluded_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_outside_grid_is_excluded(con, kernel)

    def test_single_point_outside_grid_is_excluded_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_outside_grid_is_excluded(con, kernel)

    def test_single_point_outside_grid_is_excluded_using_binned_only_fast(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_outside_grid_is_excluded(con, kernel)

    def test_single_point_outside_grid_and_one_inside_excludes_outside_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only(con, kernel)

    def test_single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only(con, kernel)

    def test_single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_outside_grid_and_one_inside_excludes_outside_using_binned_only(con, kernel)

    def test_multiple_points_inside_grid_and_outside_using_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        multiple_points_inside_grid_and_outside(con, kernel)

    def test_multiple_points_inside_grid_and_outside_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        multiple_points_inside_grid_and_outside(con, kernel)

    def test_multiple_points_inside_grid_and_outside_using_binning_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        multiple_points_inside_grid_and_outside(con, kernel)

    def test_single_point_on_grid_corner_is_counted_once(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        single_point_on_grid_corner_is_counted_once(con, kernel)
    
    def test_single_point_on_grid_corner_is_counted_once_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_on_grid_corner_is_counted_once(con, kernel)

    def test_single_point_on_grid_corner_is_counted_once_using_bined_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_on_grid_corner_is_counted_once(con, kernel)

    def test_single_point_on_grid_corner_is_counted_once_using_bined_only_fast(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_on_grid_corner_is_counted_once(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time_and_mising_samples_THEN_error(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time_and_mising_samples_THEN_error(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()
        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()
        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()
        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_no_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(self):
        con = BinningCubeCellConstraint()

        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure_binned_only(self):
        con = BinnedCubeCellOnlyConstraint()

        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure_binned_only_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()

        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(con, kernel)

    def test_data_with_no_standard_name(self):
        sample_cube = make_mock_cube()
        data_points = make_dummy_1d_ungridded_data()
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=SlowMean())[0]
    
    def test_data_with_invalid_standard_name(self):
        sample_cube = make_mock_cube()
        data_points = make_dummy_1d_ungridded_data_with_invalid_standard_name()
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=SlowMean())[0]

    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude(self):
        con = CubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_decreasing_latitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude_binned_only_con(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_decreasing_latitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude_using_binning(self):
        con = BinningCubeCellConstraint()
        kernel = SlowMean()

        single_point_results_in_single_value_in_cell_with_decreasing_latitude(con, kernel)

    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude_using_binned_fast_mean(self):
        con = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        single_point_results_in_single_value_in_cell_with_decreasing_latitude(con, kernel)

    def test_can_colocate_list_of_data(self):
        constraint = BinningCubeCellConstraint()
        kernel = SlowMean()

        can_colocate_list_of_data(constraint, kernel)

    def test_can_colocate_list_of_data_binned_only_con(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = SlowMean()

        can_colocate_list_of_data(constraint, kernel)

    def test_can_colocate_list_of_data_binned_only_con_fast_mean(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = FastMean()

        can_colocate_list_of_data(constraint, kernel)

    def test_single_moments(self):
        constraint = BinningCubeCellConstraint()
        kernel = moments()

        single_moments(constraint, kernel)

    def test_single_moments_binned_only_con(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = SlowMoments()

        single_moments(constraint, kernel)

    def test_single_moments_binned_only_con_fast_moment(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = FastMoments()

        single_moments(constraint, kernel)

    def test_list_moments(self):
        constraint = BinningCubeCellConstraint()
        kernel = moments()

        list_moments(constraint, kernel)

    def test_list_moments_binned_only_con(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = SlowMoments()

        list_moments(constraint, kernel)

    def test_list_moments_binned_only_con_fast_moment(self):
        constraint = BinnedCubeCellOnlyConstraint()
        kernel = FastMoments()

        list_moments(constraint, kernel)