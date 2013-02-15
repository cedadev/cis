'''
 Module to test the colocation routines
'''
from jasmin_cis.col import Colocator
from nose.tools import istest, eq_, assert_almost_equal
from test_util import mock

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
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0) ]
    col = Colocator(sample_points, cube,'nn')
    new_data = col.colocate()
    eq_(new_data.data[0], 8.0)
    eq_(new_data.data[1], 12.0)
    eq_(new_data.data[2], 4.0)
    
@istest
def test_already_colocated_in_col_gridded_to_ungridded_using_nn_in_2d():
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    cube = mock.make_square_3x3_2d_cube()
    # This point already exists on the cube with value 5 - which shouldn't be a problem
    sample_points = [ HyperPoint(0.0, 0.0) ]
    col = Colocator(sample_points, cube,'nn')
    new_data = col.colocate()
    eq_(new_data.data[0], 8.0)
    
@istest
def test_coordinates_exactly_between_points_in_col_gridded_to_ungridded_using_nn_in_2d():
    '''
        This works out the edge case where the points are exactly in the middle or two or more datapoints.
            Iris seems to count a point as 'belonging' to a datapoint if it is greater than a datapoint cell's lower
            bound and less than or equal to it's upper bound. Where a cell is an imaginary boundary around a datapoint
            which divides the grid.
    '''
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5) ]
    col = Colocator(sample_points, cube,'nn')
    new_data = col.colocate()
    eq_(new_data.data[0], 8.0)
    eq_(new_data.data[1], 5.0)
    eq_(new_data.data[2], 7.0)
    eq_(new_data.data[3], 4.0)
    
@istest
def test_coordinates_outside_grid_in_col_gridded_to_ungridded_using_nn_in_2d():
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5) ]
    col = Colocator(sample_points, cube,'nn')
    new_data = col.colocate()
    eq_(new_data.data[0], 12.0)
    eq_(new_data.data[1], 6.0)
    eq_(new_data.data[2], 10.0)
    eq_(new_data.data[3], 4.0)

@istest
def can_col_gridded_to_ungridded_using_li_in_2d():
    cube = mock.make_dummy_2d_cube()
    sample_points = mock.make_dummy_2d_points_list(20)
    col = Colocator(sample_points, cube,'li')
    col.colocate()
    assert(is_colocated(col.points, sample_points))

@istest
def test_basic_col_gridded_to_ungridded_using_li_in_2d():
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    cube = mock.make_square_3x3_2d_cube()
    sample_points = [ HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0) ]
    col = Colocator(sample_points, cube,'li')
    new_data = col.colocate()
    assert_almost_equal(new_data.data[0], 8.8)
    assert_almost_equal(new_data.data[1], 11.2)
    assert_almost_equal(new_data.data[2], 4.8)
