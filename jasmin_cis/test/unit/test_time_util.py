"""
module to test the time conversion utilities
"""
from nose.tools import istest, raises, eq_, assert_almost_equal
import numpy as np
import datetime as dt

from jasmin_cis.time_util import *

sec = 1.0/(24.0*60.0*60.0)
days_since_standard_epoch = 143541.0 # Almost, but not quite 365.2425*393.0, not sure why...

@istest
def test_that_can_convert_tai_to_datetime_obj():
    a = np.arange(6).reshape(2,3)
    b= convert_sec_since_to_std_time_array(a,dt.datetime(1993,1,1))
    eq_(a.shape,b.shape)
    assert_almost_equal(b[0][0],days_since_standard_epoch)
    assert_almost_equal(b[0][1],days_since_standard_epoch+1*sec)
    assert_almost_equal(b[0][2],days_since_standard_epoch+2*sec)
    assert_almost_equal(b[1][0],days_since_standard_epoch+3*sec)
    assert_almost_equal(b[1][1],days_since_standard_epoch+4*sec)
    assert_almost_equal(b[1][2],days_since_standard_epoch+5*sec)


@istest
def test_that_can_parse_datetimestr_to_obj():
    # when not specifying the hours, minutes or seconds, 0 is used
    eq_(parse_datetimestr_to_std_time("2010-02-05 02:15:45"),convert_datetime_to_std_time(dt.datetime(2010,02,05,02,15,45)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02:15"),convert_datetime_to_std_time(dt.datetime(2010,02,05,02,15,0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02"),convert_datetime_to_std_time(dt.datetime(2010,02,05,02,0,0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05"),convert_datetime_to_std_time(dt.datetime(2010,02,05,0,0,0)))

    # GOTCHA: when not specifying an element of a date (i.e. the year, month or day), the current date is used
    now = dt.datetime.now()
    eq_(parse_datetimestr_to_std_time("2010-02-05"),convert_datetime_to_std_time(dt.datetime(2010,02,05)))
    eq_(parse_datetimestr_to_std_time("2010-02"),convert_datetime_to_std_time(dt.datetime(2010,02,now.day)))
    eq_(parse_datetimestr_to_std_time("2010-"),convert_datetime_to_std_time(dt.datetime(2010,now.month,now.day)))
    eq_(parse_datetimestr_to_std_time(""),convert_datetime_to_std_time(dt.datetime(now.year,now.month,now.day)))


@istest
def test_that_can_parse_time_deltas():
    delta = parse_datetimestr_delta_to_float_days("P2y15m3dT5M10H3S")
    assert_almost_equal(1190.45829861, delta)

@istest
@raises(ValueError)
def test_that_raise_an_error_when_datetimestr_delta_is_invalid():
    parse_datetimestr_delta_to_float_days("some wierd string")


def test_that_can_calculate_mid_point_between_two_datetime():
    t1 = convert_datetime_to_std_time(dt.datetime(2010,02,05,0,0,0))
    t2 = convert_datetime_to_std_time(dt.datetime(2010,02,06,0,0,0))
    tm = calculate_mid_time(t1,t2)
    eq_(tm,convert_datetime_to_std_time(dt.datetime(2010,02,05,12,0,0)))

