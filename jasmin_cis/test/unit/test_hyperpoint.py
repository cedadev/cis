"""
 Module to test the colocation routines
"""
from jasmin_cis.data_io.hyperpoint import HyperPoint
from nose.tools import assert_almost_equal, istest, eq_


@istest
def test_same_point_in_space_and_time_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, val=14.4).same_point_in_space_and_time(
           HyperPoint(lat=10.0, lon=50.0, val=15.1)))


@istest
def test_is_not_same_point_in_space_and_time_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=51.0, val=14.4).same_point_in_space_and_time(
               HyperPoint(lat=10.0, lon=50.0, val=15.1)))


@istest
def test_same_point_in_space_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=10.0, val=14.4).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, alt=10.0, val=15.1)))


@istest
def test_is_notsame_point_in_space_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=10.0, val=14.4).same_point_in_space(
               HyperPoint(lat=10.0, lon=50.0, alt=11.0, val=15.1)))


@istest
def test_same_point_in_space_with_pressure_not_altitude_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, pres=10.0, val=14.4).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, pres=10.0, val=15.1)))


@istest
def test_is_not_same_point_in_space_with_pressure_not_altitude_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, pres=10.0, val=14.4).same_point_in_space(
               HyperPoint(lat=10.0, lon=50.0, pres=11.0, val=15.1)))


@istest
def test_same_point_in_space_with_pressure_and_altitude_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, val=14.4).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, val=15.1)))


@istest
def test_is_not_same_point_in_space_with_pressure_and_altitude_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, val=14.4).same_point_in_space(
               HyperPoint(lat=10.0, lon=50.0, alt=6.0, pres=11.0, val=15.1)))


@istest
def test_same_point_in_space_with_points_with_different_times():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=10.0, t=500.0).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, alt=10.0, t=501.0)))


@istest
def test_is_not_same_point_in_space_with_points_with_different_times():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=10.0, t=500.0).same_point_in_space(
               HyperPoint(lat=11.0, lon=51.0, alt=10.0, t=501.0)))


@istest
def test_same_point_in_space_with_pressure_not_altitude_with_points_with_different_times():
    assert(HyperPoint(lat=10.0, lon=50.0, pres=10.0, t=500.0).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, pres=10.0, t=501.0)))


@istest
def test_is_not_same_point_in_space_with_pressure_not_altitude_with_points_with_different_times():
    assert(not HyperPoint(lat=10.0, lon=50.0, pres=10.0, t=500.0).same_point_in_space(
               HyperPoint(lat=10.0, lon=50.0, pres=11.0, t=501.0)))


@istest
def test_same_point_in_space_with_pressure_and_altitude_with_points_with_different_times():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, t=500.0).same_point_in_space(
           HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, t=501.0)))


@istest
def test_is_not_same_point_in_space_with_pressure_and_altitude_with_points_with_different_times():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=10.0, t=500.0).same_point_in_space(
               HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=11.0, t=501.0)))


@istest
def test_same_point_in_time_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=500.0, val=14.4).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=500.0, val=15.1)))


@istest
def test_is_not_same_point_in_time_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=500.0, val=14.4).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=501.0, val=15.1)))


@istest
def test_same_point_in_time_with_pressure_not_altitude_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=500.0, val=14.4).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=500.0, val=15.1)))


@istest
def test_is_not_same_point_in_time_with_pressure_not_altitude_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=500.0, val=14.4).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=501.0, val=15.1)))


@istest
def test_same_point_in_time_with_pressure_and_altitude_with_points_with_different_values():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=5.0, t=500.0, val=14.4).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=5.0, t=500.0, val=15.1)))


@istest
def test_is_not_same_point_in_time_with_pressure_and_altitude_with_points_with_different_values():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=5.0, t=500.0, val=14.4).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=5.0, t=501.0, val=15.1)))


@istest
def test_same_point_in_time_with_points_with_different_spatial_coords():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=500.0).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, alt=10.0, t=500.0)))


@istest
def test_is_not_same_point_in_time_with_points_with_different_spatial_coords():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=5.0, t=500.0).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, alt=10.0, t=501.0)))


@istest
def test_same_point_in_time_with_pressure_not_altitude_with_points_with_different_spatial_coords():
    assert(HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=500.0).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, pres=10.0, t=500.0)))


@istest
def test_is_not_same_point_in_time_with_pressure_not_altitude_with_points_with_different_spatial_coords():
    assert(not HyperPoint(lat=10.0, lon=50.0, pres=5.0, t=500.0).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, pres=10.0, t=501.0)))


@istest
def test_same_point_in_time_with_pressure_and_altitude_with_points_with_different_spatial_coords():
    assert(HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=4.0, t=500.0).same_point_in_time(
           HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=9.0, t=500.0)))


@istest
def test_is_not_same_point_in_time_with_pressure_and_altitude_with_points_with_different_spatial_coords():
    assert(not HyperPoint(lat=10.0, lon=50.0, alt=5.0, pres=4.0, t=500.0).same_point_in_time(
               HyperPoint(lat=10.0, lon=50.0, alt=10.0, pres=9.0, t=501.0)))


@istest
def can_get_valid_coord_tuple_lat():
    eq_(HyperPoint(10).get_coord_tuple(), [('latitude',10)])


@istest
def can_get_valid_coord_tuple_lat_lon():
    eq_(HyperPoint(10,12).get_coord_tuple(), [('latitude',10), ('longitude',12)])


@istest
def check_furthest_point_on_equator():
    eq_(HyperPoint(0,0).furthest_point_from(),HyperPoint(0,180))


@istest
def check_furthest_point_on_pole():
    eq_(HyperPoint(90,0).furthest_point_from(),HyperPoint(-90,180))


@istest
def check_furthest_point():
    eq_(HyperPoint(51,0).furthest_point_from(),HyperPoint(-51,180))


@istest
def check_dist_between_2d_points_on_equator():
    assert_almost_equal(HyperPoint(0,0).haversine_dist(HyperPoint(0, 1)),111.317,places=3)


@istest
def check_dist_between_2d_points_at_pole():
    assert_almost_equal(HyperPoint(90,0).haversine_dist(HyperPoint(90, 1)),0.0000,places=5)


@istest
def check_dist_between_opposite_2d_points():
    """
        The distance between two points on opposite sides of the globe should be half the circumfrence of the globe
    """
    import math
    R_E = 6378 # Radius of the earth in km
    max_dist = math.pi*R_E
    assert_almost_equal(HyperPoint(0,0).haversine_dist(HyperPoint(0, 180)), max_dist, places=3)
    assert_almost_equal(HyperPoint(90,0).haversine_dist(HyperPoint(-90, 0)), max_dist, places=3)
    assert_almost_equal(HyperPoint(51,0).haversine_dist(HyperPoint(-51, 180)), max_dist, places=3)


@istest
def check_compdist_returns_true_when_p2_is_closer_than_p1():
    assert(HyperPoint(0,0).compdist(HyperPoint(4,4), HyperPoint(3,3)))


@istest
def check_compdist_returns_false_when_p1_is_closer_than_p2():
    assert( not HyperPoint(0,0).compdist(HyperPoint(3,3), HyperPoint(4,4)))


@istest
def check_compdist_returns_false_when_p1_is_the_same_as_p2():
    assert( not HyperPoint(0,0).compdist(HyperPoint(3,3), HyperPoint(3,3)))
    assert( not HyperPoint(0,0).compdist(HyperPoint(-3,3), HyperPoint(3,3)))
    assert( not HyperPoint(0,0).compdist(HyperPoint(3,-3), HyperPoint(3,3)))
    assert( not HyperPoint(0,0).compdist(HyperPoint(-3,-3), HyperPoint(3,3)))
    assert( not HyperPoint(-2.5,0).compdist(HyperPoint(-5,0), HyperPoint(0,0)))
    assert( not HyperPoint(0,-2.5).compdist(HyperPoint(0,-5), HyperPoint(0,0)))
    assert( not HyperPoint(-2.5,-2.5).compdist(HyperPoint(-5,-5), HyperPoint(0,0)))