from nose.tools import istest, raises
import datetime
import numpy
from jasmin_cis.data_io.Coord import CoordList
from jasmin_cis.col_implementations import GeneralGriddedColocator, mean, CubeCellConstraint, \
    BinningCubeCellConstraint
from jasmin_cis.test.test_util.mock import make_mock_cube, make_dummy_ungridded_data_single_point, \
    make_dummy_ungridded_data_two_points_with_different_values, make_dummy_1d_ungridded_data, \
    make_dummy_1d_ungridded_data_with_invalid_standard_name, make_square_5x3_2d_cube_with_time, \
    make_square_5x3_2d_cube_with_altitude, make_square_5x3_2d_cube_with_pressure, \
    make_square_5x3_2d_cube_with_decreasing_latitude


@istest
@raises(ValueError)
def test_throws_value_error_with_empty_coord_list():
    sample_cube = make_mock_cube()
    empty_coord_list = CoordList()

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    try:
        col.colocate(points=sample_cube, data=empty_coord_list, constraint=con, kernel=mean())[0]
    except ValueError:
        raise


@istest
def test_fill_value_for_cube_cell_constraint():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_fill_value_for_cube_cell_constraint_default_fill_value():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint()

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[float('Inf'), float('Inf'), float('Inf')],
                                   [float('Inf'), float('Inf'), float('Inf')],
                                   [float('Inf'), float('Inf'), float('Inf')],
                                   [float('Inf'), float('Inf'), float('Inf')],
                                   [float('Inf'), float('Inf'), float('Inf')]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_two_points_in_a_cell_results_in_mean_value_in_cell():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_two_points_with_different_values(0.5, 0.5, 1.2, 1.4)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.3, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result)


@istest
def test_two_points_in_a_cell_results_in_mean_value_in_cell_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_two_points_with_different_values(0.5, 0.5, 1.2, 1.4)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.3, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lat_boundary_appears_in_higher_cell():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 0.0, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lat_boundary_appears_in_higher_cell_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 0.0, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lon_boundary_appears_in_higher_cell():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.0, 2.5, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lon_boundary_appears_in_higher_cell_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(0.0, 2.5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lat_lon_boundary_appears_in_highest_cell():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 2.5, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_point_on_a_lat_lon_boundary_appears_in_highest_cell_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(2.5, 2.5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)


@istest
def test_single_point_outside_grid_is_excluded():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(99, 99, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_outside_grid_is_excluded_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(99, 99, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_on_grid_corner_is_counted_once():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(10, 5, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_on_grid_corner_is_counted_once_using_binning():
    sample_cube = make_mock_cube()
    data_point = make_dummy_ungridded_data_single_point(10, 5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, 1.2]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time():
    sample_cube = make_square_5x3_2d_cube_with_time()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time():
    sample_cube = make_square_5x3_2d_cube_with_time()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0))

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

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

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude():
    sample_cube = make_square_5x3_2d_cube_with_altitude()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    print sample_cube.data

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude():
    sample_cube = make_square_5x3_2d_cube_with_altitude()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, altitude=1.0)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

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

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure():
    sample_cube = make_square_5x3_2d_cube_with_pressure()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    print sample_cube.data

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure():
    sample_cube = make_square_5x3_2d_cube_with_pressure()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, pressure=1.0)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

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

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_data_with_no_standard_name():
    sample_cube = make_mock_cube()
    data_points = make_dummy_1d_ungridded_data()

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=mean())[0]


@istest
def test_data_with_invalid_standard_name():
    sample_cube = make_mock_cube()
    data_points = make_dummy_1d_ungridded_data_with_invalid_standard_name()

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=mean())[0]


@istest
def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude():
    sample_cube = make_square_5x3_2d_cube_with_decreasing_latitude()
    data_point = make_dummy_ungridded_data_single_point(3.0, 0.5, 1.2)

    col = GeneralGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)


@istest
def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude_using_binning():
    sample_cube = make_square_5x3_2d_cube_with_decreasing_latitude()
    data_point = make_dummy_ungridded_data_single_point(3.0, 0.5, 1.2)

    col = GeneralGriddedColocator()
    con = BinningCubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert numpy.array_equal(out_cube.data.filled(), expected_result)
