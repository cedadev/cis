"""Tests for subset_constraint module
"""
import datetime
from nose.tools import istest, raises

import numpy as np

import jasmin_cis.subsetting.subset_constraint as subset_constraint
import jasmin_cis.test.test_util.mock
import jasmin_cis.time_util as time_util


# Tests for subsetting gridded data
@istest
def can_subset_2d_gridded_data_by_longitude():
    data = jasmin_cis.test.test_util.mock.make_square_5x3_2d_cube()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [[2, 3], [5, 6], [8, 9], [11, 12], [14, 15]])


@istest
def can_subset_2d_gridded_data_by_longitude_with_wrapping_at_180():
    data = jasmin_cis.test.test_util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9)
    long_coord = data.coord('longitude')
    long_coord.points = np.array([-180., -135., -90., -45., 0., 45., 90., 135., 180.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 135.0, -90.0, True)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [[1, 2, 3, 8, 9],
                                    [10, 11, 12, 17, 18],
                                    [19, 20, 21, 26, 27],
                                    [28, 29, 30, 35, 36],
                                    [37, 38, 39, 44, 45]])


@istest
def can_subset_2d_gridded_data_by_longitude_with_wrapping_at_360():
    data = jasmin_cis.test.test_util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9)
    long_coord = data.coord('longitude')
    long_coord.points = np.array([0., 45., 90., 135., 180., 225., 270., 315., 360.])
    long_coord.bounds = None
    long_coord.guess_bounds()
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 315.0, 90.0, True)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [[1, 2, 3, 8, 9],
                                    [10, 11, 12, 17, 18],
                                    [19, 20, 21, 26, 27],
                                    [28, 29, 30, 35, 36],
                                    [37, 38, 39, 44, 45]])


@istest
def can_subset_2d_gridded_data_with_missing_data():
    """This test just shows that missing values do not interfere with subsetting -
    nothing special happens to the missing values.
    """
    data = jasmin_cis.test.test_util.mock.make_square_5x3_2d_cube_with_missing_data()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist(fill_value=-999) == [[2, 3], [-999, 6], [8, -999], [11, 12], [14, 15]])


@istest
def can_subset_2d_gridded_data_by_longitude_latitude():
    data = jasmin_cis.test.test_util.mock.make_square_5x3_2d_cube()
    long_coord = data.coord('longitude')
    lat_coord = data.coord('latitude')
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    constraint.set_limit(lat_coord, -5.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [[5, 6], [8, 9], [11, 12]])


@istest
def empty_subset_of_gridded_data_returns_no_data():
    """Checks that the convention of returning None if subsetting results in an empty subset.
    """
    data = jasmin_cis.test.test_util.mock.make_square_5x3_2d_cube()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.GriddedSubsetConstraint()
    constraint.set_limit(long_coord, 1.0, 3.0, False)
    subset = constraint.constrain(data)
    assert(subset is None)


# Tests for subsetting ungridded data
@istest
def can_subset_2d_ungridded_data_by_longitude():
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [2, 3, 5, 6, 8, 9, 11, 12, 14, 15])


@istest
def can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_180():
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data(
        lat_dim_length=5, lon_dim_length=9, lon_min=-180., lon_max=180.)
    long_coord = data.coord('longitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 135.0, -90.0, True)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [1, 2, 3, 8, 9,
                                    10, 11, 12, 17, 18,
                                    19, 20, 21, 26, 27,
                                    28, 29, 30, 35, 36,
                                    37, 38, 39, 44, 45])


@istest
def can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_360():
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data(
        lat_dim_length=5, lon_dim_length=9, lon_min=0., lon_max=360.)
    long_coord = data.coord('longitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 315.0, 90.0, True)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [1, 2, 3, 8, 9,
                                    10, 11, 12, 17, 18,
                                    19, 20, 21, 26, 27,
                                    28, 29, 30, 35, 36,
                                    37, 38, 39, 44, 45])


@istest
def can_subset_2d_ungridded_data_by_longitude_latitude():
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data()
    long_coord = data.coord('longitude')
    lat_coord = data.coord('latitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    constraint.set_limit(lat_coord, -5.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [5, 6, 8, 9, 11, 12])


@istest
def empty_subset_of_ungridded_data_returns_no_data():
    """Checks that the convention of returning None if subsetting results in an empty subset.
    """
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 1.0, 3.0, False)
    subset = constraint.constrain(data)
    assert(subset is None)


@istest
def can_subset_ungridded_data_by_time():
    data = jasmin_cis.test.test_util.mock.make_regular_4d_ungridded_data()
    time_coord = data.coord('time')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(time_coord,
                         time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 28)),
                         time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 29)), False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [2, 3, 7, 8, 12, 13, 17, 18, 22, 23, 27, 28, 32, 33, 37, 38, 42, 43, 47, 48])


@istest
def can_subset_ungridded_data_by_time_altitude():
    data = jasmin_cis.test.test_util.mock.make_regular_4d_ungridded_data()
    time_coord = data.coord('time')
    alt_coord = data.coord('altitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(time_coord,
                         time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 28)),
                         time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 29)), False)
    constraint.set_limit(alt_coord, 45.0, 75.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [27, 28, 32, 33, 37, 38])


@istest
def can_subset_2d_ungridded_data_with_missing_values():
    data = jasmin_cis.test.test_util.mock.make_regular_2d_ungridded_data_with_missing_values()
    long_coord = data.coord('longitude')
    constraint = subset_constraint.UngriddedSubsetConstraint()
    constraint.set_limit(long_coord, 0.0, 5.0, False)
    subset = constraint.constrain(data)
    assert(subset.data.tolist() == [2, 3, -999, 6, 8, -999, 11, 12, 14, 15])


if __name__ == '__main__':
    import nose
    nose.runmodule()
