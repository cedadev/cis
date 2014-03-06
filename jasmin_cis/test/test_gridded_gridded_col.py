from nose.tools import istest
import numpy
from col_implementations import GriddedColocator, gridded_gridded_nn, gridded_gridded_li
from test.test_util.mock import make_dummy_2d_cube, make_dummy_2d_cube_with_small_offset_in_lat_and_lon, \
    make_dummy_2d_cube_with_small_offset_in_lat, make_dummy_2d_cube_with_small_offset_in_lon, \
    make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres, \
    make_square_5x3_2d_cube, make_square_5x3_2d_cube_with_time


def check_cubes_have_equal_data_values(cube1, cube2, tolerance=1e-15):
    """
    Check two cubes, which have the same shape, have the same data values to within a given tolerance
    @param cube1: A cube
    @param cube2: Another cube
    @param tolerance: The amount of difference allowed in the data values
    @return: Boolean True if equal, else False
    """

    if numpy.allclose(cube1.data, cube2.data, atol=tolerance):
        return True

    return False


def check_cubes_have_equal_dimension_coordinates(cube1, cube2):
    """
    Check all the coordinates for cube 1 are identical in cube 2, but not that all the the coordinates in cube 2 are
    contained in cube 1.
    @param cube1: A cube
    @param cube2: Another cube
    @return: Boolean True if equal, else False
    """
    for coord_i in cube1.coords():
        match = False
        for coord_j in cube2.coords():
            if coord_i.name() == coord_j.name() and (coord_i.points == coord_j.points).all():
                match = True
        if not match:
            return False

    return True


def check_cubes_have_equal_data_values_and_dimension_coordinates(cube1, cube2):

    return check_cubes_have_equal_data_values(cube1, cube2) and \
        check_cubes_have_equal_dimension_coordinates(cube1, cube2)


@istest
def test_gridded_gridded_nn_for_same_grids_check_returns_original_data():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_nn():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube_with_small_offset_in_lat_and_lon()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    assert check_cubes_have_equal_data_values(data_cube, out_cube)
    assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
    assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
    assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_for_two_grids_offset_by_half_grid_spacing_using_nn():
    sample_cube, data_cube = make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    result = numpy.array([[0., 0., 1., 0., 1.],
                          [0., 0., 1., 0., 1.],
                          [1., 1., 0., 1., 0.],
                          [0., 0., 1., 0., 1.],
                          [1., 1., 0., 1., 0.]])

    assert (out_cube.data == result).all()


@istest
def test_gridded_gridded_li_for_same_grids_check_returns_original_data():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

    assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_using_li():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube_with_small_offset_in_lat()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

    # Need some asserts once the test can actually run...


@istest
def test_gridded_gridded_for_one_grid_with_slight_offset_in_lon_using_li():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube_with_small_offset_in_lon()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

    assert check_cubes_have_equal_data_values(data_cube, out_cube, tolerance=0.1)
    assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
    assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
    assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_li():
    sample_cube = make_dummy_2d_cube()
    data_cube = make_dummy_2d_cube_with_small_offset_in_lat_and_lon()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

    # Need some asserts once the test can actually run...


@istest
def test_gridded_gridded_for_two_grids_offset_by_half_grid_spacing_using_li():
    sample_cube, data_cube = make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

    expected_result = numpy.array([[-1., 2., -1., 2., -1.],
                                   [0.5, 0.5, 0.5, 0.5, 0.5],
                                   [0.5, 0.5, 0.5, 0.5, 0.5],
                                   [0.5, 0.5, 0.5, 0.5, 0.5],
                                   [0.5, 0.5, 0.5, 0.5, 0.5]])

    assert (out_cube.data == expected_result).all()
    assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)


@istest
def test_gridded_gridded_nn_with_one_grid_containing_time():
    sample_cube = make_square_5x3_2d_cube()
    data_cube = make_square_5x3_2d_cube_with_time()

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_nn_with_one_grid_containing_time_and_slightly_offset():
    sample_cube = make_square_5x3_2d_cube()
    data_cube = make_square_5x3_2d_cube_with_time(offset=0.1)

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    assert check_cubes_have_equal_data_values(data_cube, out_cube)
    assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
    assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)


@istest
def test_gridded_gridded_nn_with_one_grid_containing_time_and_moderate_offset():
    sample_cube = make_square_5x3_2d_cube()
    data_cube = make_square_5x3_2d_cube_with_time(offset=2.6)

    col = GriddedColocator()

    out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

    expected_result = numpy.array([[[1., 2., 3., 4., 5., 6., 7.],
                                    [1., 2., 3., 4., 5., 6., 7.],
                                    [8., 9., 10., 11., 12., 13., 14.]],

                                   [[1., 2., 3., 4., 5., 6., 7.],
                                    [1., 2., 3., 4., 5., 6., 7.],
                                    [8., 9., 10., 11., 12., 13., 14.]],

                                   [[22., 23., 24., 25., 26., 27., 28.],
                                    [22., 23., 24., 25., 26., 27., 28.],
                                    [29., 30., 31., 32., 33., 34., 35.]],

                                   [[43., 44., 45., 46., 47., 48., 49.],
                                    [43., 44., 45., 46., 47., 48., 49.],
                                    [50., 51., 52., 53., 54., 55., 56.]],

                                   [[64., 65., 66., 67., 68., 69., 70.],
                                    [64., 65., 66., 67., 68., 69., 70.],
                                    [71., 72., 73., 74., 75., 76., 77.]]])

    assert (out_cube.data == expected_result).all()
    assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
