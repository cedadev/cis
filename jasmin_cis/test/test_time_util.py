"""
module to test the time conversion utilities
"""
from nose.tools import istest, raises, eq_
import numpy as np
import datetime as dt

from jasmin_cis.time_util import *

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
def test_that_can_parse_datetimestr_to_obj():
    # when not specifying the hours, minutes or seconds, 0 is used
    eq_(parse_datetimestr_to_obj("2010-02-05 02:15:45"),dt.datetime(2010,02,05,02,15,45))
    eq_(parse_datetimestr_to_obj("2010-02-05 02:15"),dt.datetime(2010,02,05,02,15,0))
    eq_(parse_datetimestr_to_obj("2010-02-05 02"),dt.datetime(2010,02,05,02,0,0))
    eq_(parse_datetimestr_to_obj("2010-02-05"),dt.datetime(2010,02,05,0,0,0))

    # GOTCHA: when not specifying an element of a date (i.e. the year, month or day), the current date is used
    now = dt.datetime.now()
    eq_(parse_datetimestr_to_obj("2010-02-05"),dt.datetime(2010,02,05))
    eq_(parse_datetimestr_to_obj("2010-02"),dt.datetime(2010,02,now.day))
    eq_(parse_datetimestr_to_obj("2010-"),dt.datetime(2010,now.month,now.day))
    eq_(parse_datetimestr_to_obj(""),dt.datetime(now.year,now.month,now.day))

@istest
def test_that_can_parse_time_deltas():
    delta = parse_datetimestr_delta_to_obj("2y15m3d")
    eq_(delta.years,3)
    eq_(delta.months,3)
    eq_(delta.days,3)
    eq_(delta.hours,0)
    eq_(delta.minutes,0)
    eq_(delta.seconds,0)

@istest
@raises(ValueError)
def test_that_raise_an_error_when_datetimestr_delta_is_invalid():
    parse_datetimestr_delta_to_obj("some wierd string")

