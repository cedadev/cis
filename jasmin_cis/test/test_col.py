'''
 Module to test the colocation routines
'''
from jasmin_cis.col import Colocator, HyperPoint
from nose.tools import istest, raises, eq_
from test_util import mock
from jasmin_cis.exceptions import *

def is_colocated(data1, data2):
    '''
        Checks wether two datasets share all of the same points, this might be useful
        to determine if colocation is necesary or completed succesfully
    '''
    colocated = len(data1) == len(data2)
    if colocated:
        for i, point1 in enumerate(data1):
            colocated = point1.same_point_in_space_and_time(data2[i])
            if not colocated:
                return colocated
    return colocated

@istest
def test_same_point_in_space_and_time_with_points_with_different_values():
    assert(HyperPoint(10.0,50.0,val=14.4).same_point_in_space_and_time(HyperPoint(10.0,50.0,val=15.1)))

@istest
def can_get_valid_coord_tuple():
    from jasmin_cis.col import get_coord_tuple
    eq_(get_coord_tuple(HyperPoint(10)), [('latitude',10)])

@istest
def can_col_gridded_to_ungridded_using_nn_in_1d():
    cube = mock.make_dummy_1d_cube()
    sample_points = mock.make_dummy_1d_points_list(20)
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    assert(is_colocated(col.points, sample_points))
    
@istest
def can_col_gridded_to_ungridded_using_nn_in_2d():
    cube = mock.make_dummy_2d_cube()
    sample_points = mock.make_dummy_2d_points_list(20)
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    assert(is_colocated(col.points, sample_points))
    
@istest
def test_basic_col_gridded_to_ungridded_using_nn_in_2d():
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0) ]
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    eq_(col.points[0].val[0], 8.0)
    eq_(col.points[1].val[0], 12.0)    
    eq_(col.points[2].val[0], 4.0)        
    
@istest
def test_already_colocated_in_col_gridded_to_ungridded_using_nn_in_2d():
    cube = mock.make_square_3x3_2d_cube()
    # This point already exists on the cube with value 5 - which shouldn't be a problem
    sample_points = [ HyperPoint(0.0, 0.0) ]
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    eq_(col.points[0].val[0], 8.0)
    
@istest
def test_coordinates_exactly_between_points_in_col_gridded_to_ungridded_using_nn_in_2d():
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5) ]
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    eq_(col.points[0].val[0], 8.0)
    eq_(col.points[1].val[0], 8.0)
    eq_(col.points[2].val[0], 8.0)
    eq_(col.points[3].val[0], 8.0)
    
@istest
def test_coordinates_outside_grid_in_col_gridded_to_ungridded_using_nn_in_2d():
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5) ]
    col = Colocator(sample_points, cube,'nn')
    col.colocate()
    eq_(col.points[0].val[0], 12.0)
    eq_(col.points[1].val[0], 6.0)
    eq_(col.points[2].val[0], 10.0)
    eq_(col.points[3].val[0], 4.0)

