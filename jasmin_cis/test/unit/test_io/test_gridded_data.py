"""Tests for ungridded_data module
See also test_hyperpoint_view.
"""
from nose.tools import istest, nottest, raises
import numpy as np

import jasmin_cis.test.util.mock as mock
import jasmin_cis.data_io.gridded_data as gridded_data


@istest
def test_can_create_gridded_data():
    gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
    assert(gd.coord(standard_name='latitude') is not None)
    assert(gd.coord(standard_name='longitude') is not None)
    assert(gd.data.size == 15)
    assert(isinstance(gd, gridded_data.GriddedData))


@istest
def test_get_all_points_returns_points():
    gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
    points = gd.get_all_points()
    num_points = len([p for p in points])
    assert(num_points == 15)


@istest
def test_get_non_masked_points_returns_points():
    gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
    points = gd.get_non_masked_points()
    num_points = len([p for p in points])
    assert(num_points == 12)


@istest
def test_get_coordinates_points_returns_points():
    gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
    points = gd.get_coordinates_points()
    num_points = len([p for p in points])
    assert(num_points == 15)


@istest
def test_can_add_history():
    gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
    new_history = 'This is a new history entry.'
    gd.add_history(new_history)
    assert(gd.attributes['history'].find(new_history) >= 0)

@istest
def test_can_set_longitude_wrap_at_180():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([0., 45., 90., 135., 180., 225., 270., 315., 359.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(-180.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= -180.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 180.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == -180.0)
    assert(long_coord.points[4] == -1.0)
    assert(long_coord.points[5] == 0.0)
    assert(long_coord.points[8] == 135.0)
    assert(gd.data[0, 0] == 5.0)
    assert(gd.data[4, 0] == 41.0)
    assert(gd.data[0, 4] == 9.0)
    assert(gd.data[4, 4] == 45.0)
    assert(gd.data[0, 5] == 1.0)
    assert(gd.data[4, 5] == 37.0)
    assert(gd.data[0, 8] == 4.0)
    assert(gd.data[4, 8] == 40.0)

@istest
def test_can_set_longitude_wrap_at_180_2():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([0., 45., 90., 135., 179., 225., 270., 315., 359.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(-180.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= -180.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 180.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == -135.0)
    assert(long_coord.points[3] == -1.0)
    assert(long_coord.points[4] == 0.0)
    assert(long_coord.points[8] == 179.0)
    assert(gd.data[0, 0] == 6.0)
    assert(gd.data[4, 0] == 42.0)
    assert(gd.data[0, 3] == 9.0)
    assert(gd.data[4, 3] == 45.0)
    assert(gd.data[0, 4] == 1.0)
    assert(gd.data[4, 4] == 37.0)
    assert(gd.data[0, 8] == 5.0)
    assert(gd.data[4, 8] == 41.0)

@istest
def test_can_set_longitude_wrap_at_180_3():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([0., 45., 90., 135., 181., 225., 270., 315., 359.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(-180.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= -180.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 180.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == -179.0)
    assert(long_coord.points[4] == -1.0)
    assert(long_coord.points[5] == 0.0)
    assert(long_coord.points[8] == 135.0)
    assert(gd.data[0, 0] == 5.0)
    assert(gd.data[4, 0] == 41.0)
    assert(gd.data[0, 4] == 9.0)
    assert(gd.data[4, 4] == 45.0)
    assert(gd.data[0, 5] == 1.0)
    assert(gd.data[4, 5] == 37.0)
    assert(gd.data[0, 8] == 4.0)
    assert(gd.data[4, 8] == 40.0)

@istest
def test_can_set_longitude_wrap_at_360():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([-180., -135., -90., -45., 0., 45., 90., 135., 179.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(0.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= 0.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 360.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == 0.0)
    assert(long_coord.points[4] == 179.0)
    assert(long_coord.points[5] == 180.0)
    assert(long_coord.points[8] == 315.0)
    assert(gd.data[0, 0] == 5.0)
    assert(gd.data[4, 0] == 41.0)
    assert(gd.data[0, 1] == 6.0)
    assert(gd.data[4, 1] == 42.0)
    assert(gd.data[0, 4] == 9.0)
    assert(gd.data[4, 4] == 45.0)
    assert(gd.data[0, 8] == 4.0)
    assert(gd.data[4, 8] == 40.0)

@istest
def test_can_set_longitude_wrap_at_360_2():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([-180., -135., -90., -45., -1., 45., 90., 135., 179.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(0.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= 0.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 360.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == 45.0)
    assert(long_coord.points[3] == 179.0)
    assert(long_coord.points[4] == 180.0)
    assert(long_coord.points[8] == 359.0)
    assert(gd.data[0, 0] == 6.0)
    assert(gd.data[4, 0] == 42.0)
    assert(gd.data[0, 3] == 9.0)
    assert(gd.data[4, 3] == 45.0)
    assert(gd.data[0, 4] == 1.0)
    assert(gd.data[4, 4] == 37.0)
    assert(gd.data[0, 8] == 5.0)
    assert(gd.data[4, 8] == 41.0)

@istest
def test_can_set_longitude_wrap_at_360_3():
    gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
    long_coord = gd.coord('longitude')
    long_coord.points = np.array([-180., -135., -90., -45., 1., 45., 90., 135., 179.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    gd.set_longitude_range(0.0)
    assert(np.min(gd.coords(standard_name='longitude')[0].points) >= 0.0)
    assert(np.max(gd.coords(standard_name='longitude')[0].points) < 360.0)
    long_coord = gd.coord('longitude')
    assert(long_coord.points[0] == 1.0)
    assert(long_coord.points[4] == 179.0)
    assert(long_coord.points[5] == 180.0)
    assert(long_coord.points[8] == 315.0)
    assert(gd.data[0, 0] == 5.0)
    assert(gd.data[4, 0] == 41.0)
    assert(gd.data[0, 1] == 6.0)
    assert(gd.data[4, 1] == 42.0)
    assert(gd.data[0, 4] == 9.0)
    assert(gd.data[4, 4] == 45.0)
    assert(gd.data[0, 8] == 4.0)
    assert(gd.data[4, 8] == 40.0)

if __name__ == '__main__':
    import nose
    nose.runmodule()
