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
        for point1 in data1:
            colocated = all( point1 == point2 for point2 in data2 )
            if not colocated:
                return colocated
    return colocated

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