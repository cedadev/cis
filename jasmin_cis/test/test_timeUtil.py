"""
module to test the time conversion utilities
"""
from nose.tools import istest, eq_
import numpy as np
import datetime as dt

from jasmin_cis.timeUtil import *

@istest
def test_that_can_convert_tai_to_datetime_obj():
    a = np.arange(6).reshape(2,3)
    b= convert_sec_since_to_obj_array(a,dt.datetime(1993,1,1))
    eq_(a.shape,b.shape)
    eq_(b[0][0],dt.datetime(1993,1,1,0,0,0))
    eq_(b[0][1],dt.datetime(1993,1,1,0,0,1))
    eq_(b[0][2],dt.datetime(1993,1,1,0,0,2))
    eq_(b[1][0],dt.datetime(1993,1,1,0,0,3))
    eq_(b[1][1],dt.datetime(1993,1,1,0,0,4))
    eq_(b[1][2],dt.datetime(1993,1,1,0,0,5))


@istest
def test_that_needs_renaming():
    eq_(parse_datetimestr_to_obj("2010-02-05 02:15:45"),dt.datetime(2010,02,05,02,15,45))
    eq_(parse_datetimestr_to_obj("2010-02-05 02:15"),dt.datetime(2010,02,05,02,15,0))
    eq_(parse_datetimestr_to_obj("2010-02-05 02"),dt.datetime(2010,02,05,02,0,0))
    eq_(parse_datetimestr_to_obj("2010-02-05"),dt.datetime(2010,02,05,0,0,0))

@istest
def test_that_needs_renaming():
    eq_(parse_datetimestr_to_obj("2010-02-05"),dt.datetime(2010,02,05))
    eq_(parse_datetimestr_to_obj("2010-02"),dt.datetime(2010,02,))
