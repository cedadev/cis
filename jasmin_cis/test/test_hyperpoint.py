'''
 Module to test the colocation routines
'''
from jasmin_cis.col import HyperPoint
from nose.tools import istest, raises, eq_
from test_util import mock
from jasmin_cis.exceptions import *

@istest
def test_same_point_in_space_and_time_with_points_with_different_values():
    assert(HyperPoint(10.0,50.0,val=14.4).same_point_in_space_and_time(HyperPoint(10.0,50.0,val=15.1)))

@istest
def can_get_valid_coord_tuple():
    eq_(HyperPoint(10).get_coord_tuple(), [('latitude',10)])

