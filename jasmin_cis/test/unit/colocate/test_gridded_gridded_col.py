"""
Test Gridded - Gridded Colocation
"""
from unittest import TestCase
from nose.tools import istest, raises
from iris.exceptions import CoordinateNotFoundError
import numpy

from jasmin_cis.exceptions import ClassNotFoundError
from jasmin_cis.col_implementations import GriddedColocator, GriddedColocatorUsingIrisRegrid, gridded_gridded_nn, \
    gridded_gridded_li, nn_gridded
import jasmin_cis.data_io.gridded_data as gridded_data
from jasmin_cis.test.util.mock import make_dummy_2d_cube, make_dummy_2d_cube_with_small_offset_in_lat_and_lon, \
    make_dummy_2d_cube_with_small_offset_in_lat, make_dummy_2d_cube_with_small_offset_in_lon, \
    make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres, make_mock_cube


def does_coord_exist_in_cube(cube, coord):
    try:
        cube.coord(coord)
        return True
    except CoordinateNotFoundError:
        return False


class GriddedGriddedColocatorTests(object):

    def setUp(self):
        self.colocator = None

    @istest
    @raises(ClassNotFoundError)
    def invalid_kernel_throws_error(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube = gridded_data.make_from_cube(make_mock_cube())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=nn_gridded())[0]

    @istest
    def test_gridded_gridded_nn_for_same_grids_check_returns_original_data(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube = gridded_data.make_from_cube(make_mock_cube())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_nn(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=100))
        data_cube = gridded_data.make_from_cube(make_mock_cube(horizontal_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert not numpy.array_equal(data_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert not numpy.array_equal(data_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_different_grid_size_using_nn(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=100))
        data_cube = gridded_data.make_from_cube(make_mock_cube(lat_dim_length=10,
                                                               lon_dim_length=6, horizontal_offset=0.0))

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
        sample_cube = gridded_data.make_from_cube(sample_cube)
        data_cube = gridded_data.make_from_cube(data_cube)

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
        sample_cube = gridded_data.make_from_cube(make_dummy_2d_cube())
        data_cube = gridded_data.make_from_cube(make_dummy_2d_cube())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert numpy.allclose(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube = gridded_data.make_from_cube(make_dummy_2d_cube())
        data_cube = gridded_data.make_from_cube(make_dummy_2d_cube_with_small_offset_in_lat())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert numpy.allclose(data_cube.data, out_cube.data, atol=0.1)
        assert not numpy.array_equal(sample_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lon_using_li(self):
        sample_cube = gridded_data.make_from_cube(make_dummy_2d_cube())
        data_cube = gridded_data.make_from_cube(make_dummy_2d_cube_with_small_offset_in_lon())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert numpy.allclose(data_cube.data, out_cube.data, atol=0.1)
        assert not numpy.array_equal(sample_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube = gridded_data.make_from_cube(make_dummy_2d_cube())
        data_cube = gridded_data.make_from_cube(make_dummy_2d_cube_with_small_offset_in_lat_and_lon())

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert numpy.allclose(data_cube.data, out_cube.data, atol=0.2)
        assert not numpy.array_equal(sample_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_for_one_grid_with_slight_offset_in_lat_and_lon_different_grid_size_using_li(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=100))
        data_cube = gridded_data.make_from_cube(make_mock_cube(lat_dim_length=10,
                                                               lon_dim_length=6, horizontal_offset=0.0))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[1., 3.5,   6.],
                              [14.5,  17., 19.5],
                              [28., 30.5,  33.],
                              [41.5, 44.,   46.5],
                              [55., 57.5,  60.]])

        assert numpy.allclose(out_cube.data, result)

    @istest
    def test_gridded_gridded_for_two_grids_offset_by_half_grid_spacing_using_li(self):
        # Test fails on Iris 1.5.1., but passes on version 1.6.1
        sample_cube, data_cube = make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres()
        sample_cube = gridded_data.make_from_cube(sample_cube)
        data_cube = gridded_data.make_from_cube(data_cube)

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        expected_result = numpy.array([[-1.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5],
                                       [0.5, 0.5, 0.5, 0.5, 0.5]])

        assert numpy.array_equal(out_cube.data, expected_result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_li_with_one_grid_containing_altitude(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube = gridded_data.make_from_cube(make_mock_cube(alt_dim_length=7))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('altitude').points, out_cube.coord('altitude').points)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time_and_slightly_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, horizontal_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(data_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_nn_with_one_grid_containing_time_and_moderate_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, horizontal_offset=2.6))

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
        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, horizontal_offset=0.1))

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

    @istest
    def test_gridded_gridded_nn_with_sample_containing_time_and_pressure_and_small_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7,
                                                                 pres_dim_length=10, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(horizontal_offset=0.1, time_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert not does_coord_exist_in_cube(out_cube, 'time')
        assert not does_coord_exist_in_cube(out_cube, 'pressure')

    @istest
    def test_gridded_gridded_li_with_sample_grid_4d_and_slightly_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(alt_dim_length=7, time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(horizontal_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[0.92, 1.92, 2.92],
                              [3.92, 4.92, 5.92],
                              [6.92, 7.92, 8.92],
                              [9.92, 10.92, 11.92],
                              [12.92, 13.92, 14.92]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert not does_coord_exist_in_cube(out_cube, 'time')
        assert not does_coord_exist_in_cube(out_cube, 'altitude')


class TestGriddedColocatorUsingIrisRegrid(GriddedGriddedColocatorTests, TestCase):
    def setUp(self):
        self.colocator = GriddedColocatorUsingIrisRegrid()

    def test_gridded_gridded_li_for_GriddedDataList(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList

        sample_cube = gridded_data.make_from_cube(make_mock_cube(data_offset=100))
        data_cube1 = gridded_data.make_from_cube(make_mock_cube(lat_dim_length=10,
                                                                lon_dim_length=6, horizontal_offset=0.0))
        data_cube2 = gridded_data.make_from_cube(make_mock_cube(lat_dim_length=10, data_offset=3,
                                                                lon_dim_length=6, horizontal_offset=0.0))
        data_list = GriddedDataList([data_cube1, data_cube2])
        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_list, constraint=None, kernel=gridded_gridded_li())

        result = numpy.array([[1., 3.5,   6.],
                              [14.5,  17., 19.5],
                              [28., 30.5,  33.],
                              [41.5, 44.,   46.5],
                              [55., 57.5,  60.]])

        assert isinstance(out_cube, GriddedDataList)
        assert numpy.allclose(out_cube[0].data, result)
        assert numpy.allclose(out_cube[1].data, result + 3)

    @istest
    def test_gridded_gridded_nn_for_GriddedDataList(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList

        sample_cube = gridded_data.make_from_cube(make_mock_cube())
        data_cube1 = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, horizontal_offset=2.6))
        data_cube2 = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, horizontal_offset=2.6,
                                                                data_offset=3))
        data_list = GriddedDataList([data_cube1, data_cube2])
        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_list, constraint=None, kernel=gridded_gridded_nn())

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

        assert isinstance(out_cube, GriddedDataList)
        assert numpy.array_equal(out_cube[0].data, expected_result)
        assert numpy.array_equal(out_cube[1].data, expected_result + 3)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[0].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[0].coord('longitude').points)
        assert numpy.array_equal(data_list.coord('time').points, out_cube[0].coord('time').points)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[1].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[1].coord('longitude').points)
        assert numpy.array_equal(data_list.coord('time').points, out_cube[1].coord('time').points)


class TestGriddedGriddedColocator(GriddedGriddedColocatorTests, TestCase):
    """
    Contains tests that are not available to Iris Regrid colocator
    """

    def setUp(self):
        self.colocator = GriddedColocator()

    @istest
    def test_gridded_gridded_nn_with_both_grids_containing_time_and_small_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7,
                                                               horizontal_offset=0.1, time_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)

    @istest
    def test_gridded_gridded_nn_with_both_grids_containing_time_and_moderate_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7,
                                                               horizontal_offset=2.6, time_offset=1.5))

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
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7,
                                                               horizontal_offset=0.1, time_offset=0.5))

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
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
            time_offset=1.5))

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
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
            time_offset=1.5))

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

    @istest
    def test_gridded_gridded_nn_with_4d_data_and_small_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(alt_dim_length=4,
                                                                 time_dim_length=3, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(alt_dim_length=4, time_dim_length=3,
                                                horizontal_offset=0.1, altitude_offset=0.1, time_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        assert numpy.array_equal(data_cube.data, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(sample_cube.coord('altitude').points, out_cube.coord('altitude').points)

    @istest
    def test_gridded_gridded_li_with_4d_data_and_small_offset(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            alt_dim_length=2, time_dim_length=3, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            alt_dim_length=2, time_dim_length=3, horizontal_offset=0.1, altitude_offset=0.1,
            time_offset=0.1))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        result = numpy.array([[[[0.37714286, 1.37714286, 2.37714286],
                                [3.37714286, 4.37714286, 5.37714286]],

                               [[6.37714286, 7.37714286, 8.37714286],
                                [9.37714286, 10.37714286, 11.37714286]],

                               [[12.37714286, 13.37714286, 14.37714286],
                                [15.37714286, 16.37714286, 17.37714286]]],

                              [[[18.37714286, 19.37714286, 20.37714286],
                                [21.37714286, 22.37714286, 23.37714286]],

                               [[24.37714286, 25.37714286, 26.37714286],
                                [27.37714286, 28.37714286, 29.37714286]],

                               [[30.37714286, 31.37714286, 32.37714286],
                                [33.37714286, 34.37714286, 35.37714286]]],

                              [[[36.37714286, 37.37714286, 38.37714286],
                                [39.37714286, 40.37714286, 41.37714286]],

                               [[42.37714286, 43.37714286, 44.37714286],
                                [45.37714286, 46.37714286, 47.37714286]],

                               [[48.37714286, 49.37714286,  50.37714286],
                                [51.37714286, 52.37714286, 53.37714286]]],

                              [[[54.37714286, 55.37714286, 56.37714286],
                                [57.37714286, 58.37714286, 59.37714286]],

                               [[60.37714286, 61.37714286, 62.37714286],
                                [63.37714286, 64.37714286, 65.37714286]],

                               [[66.37714286, 67.37714286, 68.37714286],
                                [69.37714286, 70.37714286, 71.37714286]]],

                              [[[72.37714286, 73.37714286, 74.37714286],
                                [75.37714286, 76.37714286, 77.37714286]],

                               [[78.37714286, 79.37714286, 80.37714286],
                                [81.37714286, 82.37714286, 83.37714286]],

                               [[84.37714286, 85.37714286, 86.37714286],
                                [87.37714286, 88.37714286, 89.37714286]]]])

        assert numpy.allclose(result, out_cube.data)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(sample_cube.coord('altitude').points, out_cube.coord('altitude').points)

    @istest
    def test_gridded_gridded_li_with_sample_grid_4d_data_grid_with_time_with_moderate_offset_and_different_grids(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(pres_dim_length=3, time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
            time_offset=1.5))

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

    @istest
    def test_gridded_gridded_ni_with_data_grid_4d_sample_grid_with_time_with_moderate_offset_and_different_grids(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=3, lon_dim_length=3, alt_dim_length=2, time_dim_length=2,
            horizontal_offset=2.6, time_offset=1.5))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        result = numpy.array([[[[1., 3.],
                                [1., 3.],
                                [1., 3.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.]],

                               [[1., 3.],
                                [1., 3.],
                                [1., 3.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.]],

                               [[5., 7.],
                                [5., 7.],
                                [5., 7.],
                                [6., 8.],
                                [6., 8.],
                                [6., 8.],
                                [6., 8.]]],

                              [[[1., 3.],
                                [1., 3.],
                                [1., 3.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.]],

                               [[1., 3.],
                                [1., 3.],
                                [1., 3.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.],
                                [2., 4.]],

                               [[5., 7.],
                                [5., 7.],
                                [5., 7.],
                                [6., 8.],
                                [6., 8.],
                                [6., 8.],
                                [6., 8.]]],

                              [[[13., 15.],
                                [13., 15.],
                                [13., 15.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.]],

                               [[13., 15.],
                                [13., 15.],
                                [13., 15.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.]],

                               [[17., 19.],
                                [17., 19.],
                                [17., 19.],
                                [18., 20.],
                                [18., 20.],
                                [18., 20.],
                                [18., 20.]]],

                              [[[13., 15.],
                                [13., 15.],
                                [13., 15.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.]],

                               [[13., 15.],
                                [13., 15.],
                                [13., 15.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.],
                                [14., 16.]],

                               [[17., 19.],
                                [17., 19.],
                                [17., 19.],
                                [18., 20.],
                                [18., 20.],
                                [18., 20.],
                                [18., 20.]]],

                              [[[25., 27.],
                                [25., 27.],
                                [25., 27.],
                                [26., 28.],
                                [26., 28.],
                                [26., 28.],
                                [26., 28.]],

                               [[25., 27.],
                                [25., 27.],
                                [25., 27.],
                                [26., 28.],
                                [26., 28.],
                                [26., 28.],
                                [26., 28.]],

                               [[29., 31.],
                                [29., 31.],
                                [29., 31.],
                                [30., 32.],
                                [30., 32.],
                                [30., 32.],
                                [30., 32.]]]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(data_cube.coord('altitude').points, out_cube.coord('altitude').points)

    @istest
    def test_gridded_gridded_li_with_data_grid_4d_sample_grid_with_time_with_moderate_offset_and_different_grids(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=3, lon_dim_length=3, alt_dim_length=2, time_dim_length=2,
            horizontal_offset=2.6, time_offset=1.5))

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        # Note the result here has a different shape, (5, 3, 7, 2) to the same test that uses nn instead of li. The nn
        # test has a shape of (5, 3, 2, 7), but this should not make any difference to anything subsequently done with
        # the output.

        result = numpy.array([[[[-5.7, -4.7, -3.7, -2.7, -1.7, -0.7, 0.3],
                                [-3.7, -2.7, -1.7, -0.7,  0.3, 1.3, 2.3]],

                               [[-1.7, -0.7, 0.3, 1.3, 2.3, 3.3, 4.3],
                                [0.3, 1.3, 2.3, 3.3, 4.3, 5.3, 6.3]],

                               [[2.3, 3.3, 4.3, 5.3, 6.3, 7.3, 8.3],
                                [4.3, 5.3, 6.3, 7.3, 8.3, 9.3, 10.3]]],

                              [[[0.3, 1.3, 2.3, 3.3, 4.3, 5.3, 6.3],
                                [2.3, 3.3, 4.3, 5.3, 6.3, 7.3, 8.3]],

                               [[4.3, 5.3, 6.3, 7.3, 8.3, 9.3, 10.3],
                                [6.3, 7.3, 8.3, 9.3, 10.3, 11.3, 12.3]],

                               [[8.3, 9.3, 10.3, 11.3, 12.3, 13.3, 14.3],
                                [10.3, 11.3, 12.3, 13.3, 14.3, 15.3, 16.3]]],

                              [[[6.3, 7.3, 8.3, 9.3, 10.3, 11.3, 12.3],
                                [8.3, 9.3, 10.3, 11.3, 12.3, 13.3, 14.3]],

                               [[10.3, 11.3, 12.3, 13.3, 14.3, 15.3, 16.3],
                                [12.3, 13.3, 14.3, 15.3, 16.3, 17.3, 18.3]],

                               [[14.3, 15.3, 16.3, 17.3, 18.3, 19.3, 20.3],
                                [16.3, 17.3, 18.3, 19.3, 20.3, 21.3, 22.3]]],

                              [[[12.3, 13.3, 14.3, 15.3, 16.3, 17.3, 18.3],
                                [14.3, 15.3, 16.3, 17.3, 18.3, 19.3, 20.3]],

                               [[16.3, 17.3, 18.3, 19.3, 20.3, 21.3, 22.3],
                                [18.3, 19.3, 20.3, 21.3, 22.3, 23.3, 24.3]],

                               [[20.3, 21.3, 22.3, 23.3, 24.3, 25.3, 26.3],
                                [22.3, 23.3, 24.3, 25.3, 26.3, 27.3, 28.3]]],

                              [[[18.3, 19.3, 20.3, 21.3, 22.3, 23.3, 24.3],
                                [20.3, 21.3, 22.3, 23.3, 24.3, 25.3, 26.3]],

                               [[22.3, 23.3, 24.3, 25.3, 26.3, 27.3, 28.3],
                                [24.3, 25.3, 26.3, 27.3, 28.3, 29.3, 30.3]],

                               [[26.3, 27.3, 28.3, 29.3, 30.3, 31.3, 32.3],
                                [28.3, 29.3, 30.3, 31.3, 32.3, 33.3, 34.3]]]])

        assert numpy.allclose(out_cube.data, result)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube.coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(data_cube.coord('altitude').points, out_cube.coord('altitude').points)

    @istest
    def test_gridded_gridded_nn_with_very_different_grids(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=0, alt_dim_length=10, time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=0, pres_dim_length=6, time_dim_length=15,
            horizontal_offset=2.6, time_offset=1.5))

        # Result should maintain longitude, pressure and time, and discard latitude and altitude

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        # We will not verify the data here, just that the output has the correct shape
        assert out_cube.data.shape == (7, 3, 6)
        assert not does_coord_exist_in_cube(out_cube, 'latitude')
        assert not does_coord_exist_in_cube(out_cube, 'altitude')
        assert numpy.array_equal(data_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(data_cube.coord('air_pressure').points, out_cube.coord('air_pressure').points)

    @istest
    def test_gridded_gridded_li_with_very_different_grids(self):
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=0, alt_dim_length=10, time_dim_length=7, data_offset=1.0))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=0, pres_dim_length=6, time_dim_length=15,
            horizontal_offset=2.6, time_offset=1.5))

        # Result should maintain longitude, pressure and time, and discard latitude and altitude

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        # We will not verify the data here, just that the output has the correct shape

        # Note the result here has a different shape, (3, 6, 7) to the same test that uses nn instead of li. The nn
        # test has a shape of (7, 3, 6), but this should not make any difference to anything subsequently done with
        # the output.
        assert out_cube.data.shape == (3, 6, 7)
        assert not does_coord_exist_in_cube(out_cube, 'latitude')
        assert not does_coord_exist_in_cube(out_cube, 'altitude')
        assert numpy.array_equal(data_cube.coord('longitude').points, out_cube.coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube.coord('time').points)
        assert numpy.array_equal(data_cube.coord('air_pressure').points, out_cube.coord('air_pressure').points)

    # Tests for missing values in sample data - nearest neighbour kernel
    @istest
    def test_gridded_gridded_nn_with_different_grids_and_missing_sample_values_in_2d(self):
        mask = [[False, False, False, False, False],
                [False, True,  False, True,  False],
                [False, False, True, False, False]]
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=5, lon_dim_length=3, dim_order=['lon', 'lat'], mask=mask))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            time_dim_length=4, dim_order=['time', 'lat', 'lon']))

        # Result should have latitude, longitude and time.

        col = GriddedColocator(missing_data_for_missing_sample=True)

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        # Check that the output has the correct shape and missing values.
        # The order of the dimensions is that of data with any dimensions not in the sample cube at the end.
        assert out_cube.data.shape == (5, 3, 4)
        assert out_cube.data[1, 1, 0] is numpy.ma.masked
        assert out_cube.data[1, 1, 1] is numpy.ma.masked
        assert out_cube.data[1, 1, 2] is numpy.ma.masked
        assert out_cube.data[1, 1, 3] is numpy.ma.masked
        assert out_cube.data[2, 2, 0] is numpy.ma.masked
        assert out_cube.data[2, 2, 1] is numpy.ma.masked
        assert out_cube.data[2, 2, 2] is numpy.ma.masked
        assert out_cube.data[2, 2, 3] is numpy.ma.masked
        assert out_cube.data[3, 1, 0] is numpy.ma.masked
        assert out_cube.data[3, 1, 1] is numpy.ma.masked
        assert out_cube.data[3, 1, 2] is numpy.ma.masked
        assert out_cube.data[3, 1, 3] is numpy.ma.masked
        c = 0
        for m in out_cube.data.mask.ravel():
            if m:
                c += 1
        assert c == 12

    @istest
    def test_gridded_gridded_nn_with_different_grids_and_missing_sample_values_in_3d(self):
        mask = [[[False, False, False, False, False],
                 [False, False, False, False, False],
                 [False, False, False, False, False],
                 [False, False, False, False, False]],
                [[False, True,  False, True,  False],
                 [False, False, False, False, False],
                 [False, False, False, False, False],
                 [False, False, False, False, False]],
                [[False, False, True, False, False],
                 [False, False, False, False, False],
                 [False, False, False, False, False],
                 [False, False, False, False, False]]]
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=5, lon_dim_length=3, time_dim_length=4,
            dim_order=['lon', 'time', 'lat'], mask=mask))
        data_cube = gridded_data.make_from_cube(make_mock_cube(dim_order=['lat', 'lon']))

        # Result should have latitude and longitude.

        col = GriddedColocator(missing_data_for_missing_sample=True)

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_nn())[0]

        # Check that the output has the correct shape and missing values.
        # The order of the dimensions is that of data with any dimensions not in the sample cube at the end.
        assert out_cube.data.shape == (5, 3)
        # No masking since time coordinate has been collapsed.
        c = 0
        if numpy.ma.getmask(out_cube.data) is not numpy.ma.nomask:
            for m in out_cube.data.mask.ravel():
                if m:
                    c += 1
            assert c == 0

    # Tests for missing values in sample data - nearest neighbour kernel
    @istest
    def test_gridded_gridded_li_with_different_grids_and_missing_sample_values_1(self):
        mask = [[False, False, False, False, False],
                [False, True,  False, True,  False],
                [False, False, False, False, False]]
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=5, lon_dim_length=3, dim_order=['lon', 'lat'], mask=mask))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            time_dim_length=4, dim_order=['lat', 'time', 'lon']))

        # Result should have latitude, longitude and time.

        col = GriddedColocator(missing_data_for_missing_sample=True)

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert out_cube.data.shape == (5, 4, 3)
        assert out_cube.data[1, 0, 1] is numpy.ma.masked
        assert out_cube.data[1, 1, 1] is numpy.ma.masked
        assert out_cube.data[1, 2, 1] is numpy.ma.masked
        assert out_cube.data[1, 3, 1] is numpy.ma.masked
        assert out_cube.data[3, 0, 1] is numpy.ma.masked
        assert out_cube.data[3, 1, 1] is numpy.ma.masked
        assert out_cube.data[3, 2, 1] is numpy.ma.masked
        assert out_cube.data[3, 3, 1] is numpy.ma.masked
        c = 0
        for m in out_cube.data.mask.ravel():
            if m:
                c += 1
        assert c == 8

    @istest
    def test_gridded_gridded_li_with_different_grids_and_missing_sample_values_2(self):
        mask = [[False, False, False, False, False],
                [False, True,  False, True,  False],
                [False, False, False, False, False]]
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=5, lon_dim_length=3, dim_order=['lon', 'lat'], mask=mask))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            time_dim_length=4, dim_order=['time', 'lat', 'lon']))

        # Result should have latitude, longitude and time.

        col = GriddedColocator(missing_data_for_missing_sample=True)

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert out_cube.data.shape == (4, 5, 3)
        assert out_cube.data[0, 1, 1] is numpy.ma.masked
        assert out_cube.data[1, 1, 1] is numpy.ma.masked
        assert out_cube.data[2, 1, 1] is numpy.ma.masked
        assert out_cube.data[3, 1, 1] is numpy.ma.masked
        assert out_cube.data[0, 3, 1] is numpy.ma.masked
        assert out_cube.data[1, 3, 1] is numpy.ma.masked
        assert out_cube.data[2, 3, 1] is numpy.ma.masked
        assert out_cube.data[3, 3, 1] is numpy.ma.masked
        c = 0
        for m in out_cube.data.mask.ravel():
            if m:
                c += 1
        assert c == 8

    @istest
    def test_gridded_gridded_li_with_different_grids_and_missing_sample_values_3(self):
        mask = [[False, False, False],
                [False, False, False],
                [False, False, False],
                [False, False, True],
                [False, False, False]]
        sample_cube = gridded_data.make_from_cube(make_mock_cube(
            lat_dim_length=5, lon_dim_length=3, dim_order=['lat', 'lon'], mask=mask))
        data_cube = gridded_data.make_from_cube(make_mock_cube(
            time_dim_length=4, pres_dim_length=2, dim_order=['lon', 'pres', 'lat', 'time']))

        # Result should have latitude, longitude and time.

        col = GriddedColocator(missing_data_for_missing_sample=True)

        out_cube = col.colocate(points=sample_cube, data=data_cube, constraint=None, kernel=gridded_gridded_li())[0]

        assert out_cube.data.shape == (3, 2, 5, 4)
        assert out_cube.data[2, 0, 3, 0] is numpy.ma.masked
        assert out_cube.data[2, 0, 3, 1] is numpy.ma.masked
        assert out_cube.data[2, 0, 3, 2] is numpy.ma.masked
        assert out_cube.data[2, 0, 3, 3] is numpy.ma.masked
        assert out_cube.data[2, 1, 3, 0] is numpy.ma.masked
        assert out_cube.data[2, 1, 3, 1] is numpy.ma.masked
        assert out_cube.data[2, 1, 3, 2] is numpy.ma.masked
        assert out_cube.data[2, 1, 3, 3] is numpy.ma.masked
        c = 0
        for m in out_cube.data.mask.ravel():
            if m:
                c += 1
        assert c == 8

    def test_gridded_gridded_li_for_GriddedDataList(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList

        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))
        data_cube1 = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
            time_offset=1.5))
        data_cube2 = gridded_data.make_from_cube(make_mock_cube(
            lon_dim_length=10, lat_dim_length=6, time_dim_length=14, horizontal_offset=2.6,
            time_offset=1.5, data_offset=3))
        data_list = GriddedDataList([data_cube1, data_cube2])

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_list, constraint=None, kernel=gridded_gridded_li())

        result1 = numpy.array([[[-124.26, -123.26, -122.26, -121.26, -120.26, -119.26, -118.26],
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

        result2 = result1 + 3

        assert numpy.allclose(out_cube[0].data, result1)
        assert numpy.allclose(out_cube[1].data, result2)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[0].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[0].coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube[0].coord('time').points)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[1].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[1].coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube[1].coord('time').points)

    @istest
    def test_gridded_gridded_nn_for_GriddedDataList(self):
    # def test_gridded_gridded_nn_with_both_grids_containing_time_and_moderate_offset(self):
        from jasmin_cis.data_io.gridded_data import GriddedDataList

        sample_cube = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=1.0))

        data_cube1 = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7,
                                                                horizontal_offset=2.6, time_offset=1.5))
        data_cube2 = gridded_data.make_from_cube(make_mock_cube(time_dim_length=7, data_offset=3,
                                                                horizontal_offset=2.6, time_offset=1.5))
        data_list = GriddedDataList([data_cube1, data_cube2])

        col = self.colocator

        out_cube = col.colocate(points=sample_cube, data=data_list, constraint=None, kernel=gridded_gridded_nn())

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

        assert numpy.allclose(out_cube[0].data, result)
        assert numpy.allclose(out_cube[1].data, result + 3)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[0].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[0].coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube[0].coord('time').points)
        assert numpy.array_equal(sample_cube.coord('latitude').points, out_cube[1].coord('latitude').points)
        assert numpy.array_equal(sample_cube.coord('longitude').points, out_cube[1].coord('longitude').points)
        assert numpy.array_equal(sample_cube.coord('time').points, out_cube[1].coord('time').points)