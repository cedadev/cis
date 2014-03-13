from nose.tools import istest
import numpy
from jasmin_cis.col_implementations import GriddedColocator, GriddedColocatorUsingIrisRegrid, gridded_gridded_nn, \
    gridded_gridded_li
from jasmin_cis.test.test_util.mock import make_dummy_2d_cube, make_dummy_2d_cube_with_small_offset_in_lat_and_lon, \
    make_dummy_2d_cube_with_small_offset_in_lat, make_dummy_2d_cube_with_small_offset_in_lon, \
    make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres, make_mock_cube


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
            if coord_i.name() == coord_j.name() and numpy.array_equal(coord_i.points, coord_j.points):
                match = True
        if not match:
            return False

    return True


def check_cubes_have_equal_data_values_and_dimension_coordinates(cube1, cube2):

    return check_cubes_have_equal_data_values(cube1, cube2) and \
        check_cubes_have_equal_dimension_coordinates(cube1, cube2)


class GriddedGriddedColocatorTests():

    def __init__(self):
        self.colocator = None

    @istest
    def test_gridded_gridded_nn_for_same_grids_check_returns_original_data(self):
        sample_cube = make_mock_cube()
        data_cube = make_mock_cube()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_nn(self):
        sample_cube = make_mock_cube(data_offset=100)
        data_cube = make_mock_cube(horizontal_offset=0.1)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube)
        assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
        assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
        assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_different_grid_size_using_nn(self):
        sample_cube = make_mock_cube(data_offset=100)
        data_cube = make_mock_cube(lat_dim_length=10, lon_dim_length=6, horizontal_offset=0.0)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        result = numpy.array([[1, 3, 6],
                             [13, 15, 18],
                             [25, 27, 30],
                             [43, 45, 48],
                             [55, 57, 60]])

        assert numpy.array_equal(out_cube.data, result)

    @istest
    def test_gridded_gridded_for_two_grids_offset_by_half_grid_spacing_using_nn(self):
        sample_cube, data_cube = make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        result = numpy.array([[0., 0., 1., 0., 1.],
                              [0., 0., 1., 0., 1.],
                              [1., 1., 0., 1., 0.],
                              [0., 0., 1., 0., 1.],
                              [1., 1., 0., 1., 0.]])

        assert numpy.array_equal(out_cube.data, result)

    @istest
    def test_gridded_gridded_li_for_same_grids_check_returns_original_data(self):
        sample_cube = make_dummy_2d_cube()
        data_cube = make_dummy_2d_cube()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube = make_dummy_2d_cube()
        data_cube = make_dummy_2d_cube_with_small_offset_in_lat()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube, tolerance=0.1)
        assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
        assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
        assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lon_using_li(self):
        sample_cube = make_dummy_2d_cube()
        data_cube = make_dummy_2d_cube_with_small_offset_in_lon()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube, tolerance=0.1)
        assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
        assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
        assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube = make_dummy_2d_cube()
        data_cube = make_dummy_2d_cube_with_small_offset_in_lat_and_lon()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube, tolerance=0.2)
        assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)
        assert not check_cubes_have_equal_data_values(sample_cube, out_cube)
        assert not check_cubes_have_equal_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_different_grid_size_using_li(self):
        sample_cube = make_mock_cube(data_offset=100)
        data_cube = make_mock_cube(lat_dim_length=10, lon_dim_length=6, horizontal_offset=0.0)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[1., 3.5,   6.],
                              [14.5,  17., 19.5],
                              [28., 30.5,  33.],
                              [41.5, 44.,   46.5],
                              [55., 57.5,  60.]])

        assert numpy.array_equal(out_cube.data, result)

    @istest
    def test_gridded_gridded_for_two_grids_offset_by_half_grid_spacing_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube, data_cube = make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres()

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        expected_result = numpy.array([[-1.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5]])

        assert numpy.array_equal(out_cube.data, expected_result)
        assert check_cubes_have_equal_dimension_coordinates(sample_cube, out_cube)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time(self):
        sample_cube = make_mock_cube()
        data_cube = make_mock_cube(time_dim_length=7)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_li_with_one_grid_containing_altitude(self):
        sample_cube = make_mock_cube()
        data_cube = make_mock_cube(alt_dim_length=7)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert check_cubes_have_equal_data_values_and_dimension_coordinates(data_cube, out_cube)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time_and_slightly_offset(self):
        sample_cube = make_mock_cube(data_offset=1.0)
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=0.1)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time_and_moderate_offset(self):
        sample_cube = make_mock_cube()
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=2.6)

        col = self.colocator

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

        assert numpy.array_equal(out_cube.data, expected_result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_li_with_one_grid_containing_time_and_slightly_offset(self):
        sample_cube = make_mock_cube(data_offset=1.0)
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=0.1)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[[0.44,  1.44,  2.44,  3.44,  4.44,  5.44,  6.44],
                               [7.44,  8.44,  9.44, 10.44, 11.44, 12.44, 13.44],
                               [14.44, 15.44, 16.44, 17.44, 18.44, 19.44, 20.44]],

                              [[21.44, 22.44, 23.44, 24.44, 25.44, 26.44, 27.44],
                               [28.44, 29.44, 30.44, 31.44, 32.44, 33.44, 34.44],
                               [35.44, 36.44, 37.44, 38.44, 39.44, 40.44, 41.44]],

                              [[42.44, 43.44, 44.44, 45.44, 46.44, 47.44, 48.44],
                               [49.44, 50.44, 51.44, 52.44, 53.44, 54.44, 55.44],
                               [56.44, 57.44, 58.44, 59.44, 60.44, 61.44, 62.44]],

                              [[63.44, 64.44, 65.44, 66.44, 67.44, 68.44, 69.44],
                               [70.44, 71.44, 72.44, 73.44, 74.44, 75.44, 76.44],
                               [77.44, 78.44, 79.44, 80.44, 81.44, 82.44, 83.44]],

                              [[84.44, 85.44, 86.44, 87.44, 88.44, 89.44, 90.44],
                               [91.44, 92.44, 93.44, 94.44, 95.44, 96.44, 97.44],
                               [98.44, 99.44, 100.44, 101.44, 102.44, 103.44, 104.44]]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('time').points, out_cube.coord('time').points)


class TestGriddedColocatorUsingIrisRegrid(GriddedGriddedColocatorTests):
    def __init__(self):
        GriddedGriddedColocatorTests.__init__(self)
        self.colocator = GriddedColocatorUsingIrisRegrid()


class TestGriddedGriddedColocator(GriddedGriddedColocatorTests):
    """
    Contains tests that are not available to Iris Regrid colocator
    """

    def __init__(self):
        GriddedGriddedColocatorTests.__init__(self)
        self.colocator = GriddedColocator()

    @istest
    def test_gridded_gridded_nn_with_both_grids_containing_time_and_small_offset(self):
        sample_cube = make_mock_cube(time_dim_length=7, data_offset=1.0)
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=0.1, time_offset=0.1)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert check_cubes_have_equal_data_values(data_cube, out_cube)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_nn_with_both_grids_containing_time_and_moderate_offset(self):
        sample_cube = make_mock_cube(time_dim_length=7, data_offset=1.0)
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=2.6, time_offset=1.5)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        result = numpy.array([[[1., 1., 1., 2., 3., 4., 5.],
                               [1., 1., 1., 2., 3., 4., 5.],
                               [8., 8., 8., 9., 10., 11., 12.]],

                              [[1., 1., 1., 2., 3., 4., 5.],
                               [1., 1., 1., 2., 3., 4., 5.],
                               [8., 8., 8., 9., 10., 11., 12.]],

                              [[22., 22., 22., 23., 24., 25., 26.],
                               [22., 22., 22., 23., 24., 25., 26.],
                               [29., 29., 29., 30., 31., 32., 33.]],

                              [[43., 43., 43., 44., 45., 46., 47.],
                               [43., 43., 43., 44., 45., 46., 47.],
                               [50., 50., 50., 51., 52., 53., 54.]],

                              [[64., 64., 64., 65., 66., 67., 68.],
                               [64., 64., 64., 65., 66., 67., 68.],
                               [71., 71., 71., 72,  73., 74., 75.]]])

        assert numpy.array_equal(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_li_with_both_grids_containing_time_and_offset(self):
        sample_cube = make_mock_cube(time_dim_length=7, data_offset=1.0)
        data_cube = make_mock_cube(time_dim_length=7, horizontal_offset=0.1, time_offset=0.5)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[[-6.e-02, 9.4e-01, 1.94, 2.94, 3.94, 4.94, 5.94],
                               [6.94, 7.94, 8.94, 9.94, 1.094e+01, 1.194e+01, 1.294e+01],
                               [1.394e+01, 1.494e+01, 1.594e+01, 1.694e+01, 1.794e+01, 1.894e+01, 1.994e+01]],

                              [[2.094e+01, 2.194e+01, 2.294e+01, 2.394e+01, 2.494e+01, 2.594e+01, 2.694e+01],
                               [2.794e+01, 2.894e+01, 2.994e+01, 3.094e+01, 3.194e+01, 3.294e+01, 3.394e+01],
                               [3.494e+01, 3.594e+01, 3.694e+01, 3.794e+01, 3.894e+01, 3.994e+01, 4.094e+01]],

                              [[4.194e+01, 4.294e+01, 4.394e+01, 4.494e+01, 4.594e+01, 4.694e+01, 4.794e+01],
                               [4.894e+01, 4.994e+01, 5.094e+01, 5.194e+01, 5.294e+01, 5.394e+01, 5.494e+01],
                               [5.594e+01, 5.694e+01, 5.794e+01, 5.894e+01, 5.994e+01, 6.094e+01, 6.194e+01]],

                              [[6.294e+01, 6.394e+01, 6.494e+01, 6.594e+01, 6.694e+01, 6.794e+01, 6.894e+01],
                               [6.994e+01, 7.094e+01, 7.194e+01, 7.294e+01, 7.394e+01, 7.494e+01, 7.594e+01],
                               [7.694e+01, 7.794e+01, 7.894e+01, 7.994e+01, 8.094e+01, 8.194e+01, 8.294e+01]],

                              [[8.394e+01, 8.494e+01, 8.594e+01, 8.694e+01, 8.794e+01, 8.894e+01, 8.994e+01],
                               [9.094e+01, 9.194e+01, 9.294e+01, 9.394e+01, 9.494e+01, 9.594e+01, 9.694e+01],
                               [9.794e+01, 9.894e+01, 9.994e+01, 1.0094e+02, 1.0194e+02, 1.0294e+02, 1.0394e+02]]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_nn_with_both_grids_containing_time_with_moderate_offset_and_different_grids(self):
        sample_cube = make_mock_cube(time_dim_length=7, data_offset=1.0)
        data_cube = make_mock_cube(lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
                                   time_offset=1.5)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        result = numpy.array([[[1., 1., 1., 2., 3., 4., 5.],
                               [29., 29., 29., 30., 31., 32., 33.],
                               [99., 99., 99., 100., 101., 102., 103.]],

                              [[141., 141., 141., 142., 143., 144., 145.],
                               [169., 169., 169., 170., 171., 172., 173.],
                               [239., 239., 239., 240., 241., 242., 243.]],

                              [[281., 281., 281., 282., 283., 284., 285.],
                               [309., 309., 309., 310., 311., 312., 313.],
                               [379., 379., 379., 380., 381., 382., 383.]],

                              [[421., 421., 421., 422., 423., 424., 425.],
                               [449., 449., 449., 450., 451., 452., 453.],
                               [519., 519., 519., 520., 521., 522., 523.]],

                              [[561., 561., 561., 562., 563., 564., 565.],
                               [589., 589., 589., 590., 591., 592., 593.],
                               [659., 659., 659., 660., 661., 662., 663.]]])

        assert numpy.array_equal(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_li_with_both_grids_containing_time_with_moderate_offset_and_different_grids(self):
        sample_cube = make_mock_cube(time_dim_length=7, data_offset=1.0)
        data_cube = make_mock_cube(lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
                                   time_offset=1.5)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[[-124.26, -123.26, -122.26, -121.26, -120.26, -119.26, -118.26],
                               [-61.26, -60.26, -59.26, -58.26, -57.26, -56.26, -55.26],
                               [1.74, 2.74, 3.74, 4.74, 5.74, 6.74, 7.74]],

                              [[50.74, 51.74, 52.74, 53.74, 54.74, 55.74, 56.74],
                               [113.74, 114.74, 115.74, 116.74, 117.74, 118.74, 119.74],
                               [176.74, 177.74,  178.74,  179.74,  180.74,  181.74, 182.74]],

                              [[225.74, 226.74, 227.74, 228.74, 229.74, 230.74, 231.74],
                               [288.74, 289.74, 290.74, 291.74, 292.74, 293.74, 294.74],
                               [351.74, 352.74, 353.74, 354.74, 355.74, 356.74, 357.74]],

                              [[400.74, 401.74, 402.74, 403.74, 404.74, 405.74, 406.74],
                               [463.74, 464.74, 465.74, 466.74, 467.74, 468.74, 469.74],
                               [526.74, 527.74, 528.74, 529.74, 530.74, 531.74, 532.74]],

                              [[575.74, 576.74, 577.74, 578.74, 579.74, 580.74, 581.74],
                               [638.74,  639.74, 640.74, 641.74, 642.74, 643.74, 644.74],
                               [701.74,  702.74, 703.74, 704.74, 705.74, 706.74, 707.74]]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)