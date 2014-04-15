"""Tests for ungridded_data module
See also test_hyperpoint_view.
"""
from nose.tools import istest, nottest, raises

import jasmin_cis.test.test_util.mock as mock
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

if __name__ == '__main__':
    import nose
    nose.runmodule()
