"""Tests for parse_datetime module
"""
import datetime
from nose.tools import istest, raises, assert_almost_equal, eq_
from cis.parse_datetime import parse_datetime, parse_as_number_or_partial_datetime, find_last_day_of_month, \
                               convert_datetime_components_to_datetime, parse_datetimestr_delta_to_float_days, \
                               parse_datetimestr_to_std_time
from cis.time_util import PartialDateTime
from argparse import ArgumentTypeError


# Tests for parse_datetime
@istest
def parse_datetime_can_parse_year():
    dt = parse_as_number_or_partial_datetime('2010')
    assert (dt == PartialDateTime(2010))


@istest
def parse_datetime_can_parse_year_month():
    dt = parse_as_number_or_partial_datetime('2010-07')
    print(dt)
    assert (dt == PartialDateTime(2010, 7))


@istest
def parse_datetime_can_parse_date():
    dt = parse_as_number_or_partial_datetime('2010-07-01')
    assert (dt == PartialDateTime(2010, 7, 1))


@istest
def parse_datetime_can_parse_date_hour():
    dt = parse_as_number_or_partial_datetime('2010-07-01T13')
    assert (dt == PartialDateTime(2010, 7, 1, 13))


@istest
def parse_datetime_can_parse_date_hour_min():
    dt = parse_as_number_or_partial_datetime('2010-07-01T13:27')
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27))


@istest
def parse_datetime_can_parse_date_hour_min_sec():
    dt = parse_as_number_or_partial_datetime('2010-07-01T13:27:43')
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


@istest
def parse_datetime_can_parse_date_hour_min_sec_no_leading_zeros():
    dt = parse_as_number_or_partial_datetime('2010-3-4T5:6:7')
    assert (dt == PartialDateTime(2010, 3, 4, 5, 6, 7))


@istest
def parse_datetime_can_parse_date_time_with_space_separator():
    dt = parse_as_number_or_partial_datetime('2010-07-01 13:27:43')
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


@istest
def parse_datetime_can_parse_date_time_with_colon_separator():
    dt = parse_as_number_or_partial_datetime('2010-07-01:13:27:43')
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


# parse_datetime: Parse errors
@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_invalid_character_in_year():
    dt = parse_as_number_or_partial_datetime('2X10')


@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_time_but_incomplete_date():
    dt = parse_as_number_or_partial_datetime('2010-10T12:00')


@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_too_many_date_components():
    dt = parse_as_number_or_partial_datetime('2010-10-05-06')


@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_too_many_time_components():
    dt = parse_as_number_or_partial_datetime('2010-10-05T12:01:02:03')


# parse_datetime: Strings that parse correctly but correspond to invalid date/times
@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_invalid_month():
    dt = parse_as_number_or_partial_datetime('2010-13')


@istest
@raises(ArgumentTypeError)
def parse_datetime_raises_error_if_invalid_day():
    dt = parse_as_number_or_partial_datetime('2010-06-31')


# Tests for parse_as_number_or_datetime
@istest
def parse_as_number_or_datetime_can_parse_date_as_datetime():
    from datetime import datetime
    dt = parse_as_number_or_partial_datetime('2010-07-01')
    assert (datetime(*dt) == datetime(2010, 7, 1))


@istest
def parse_as_number_or_datetime_can_parse_integer():
    dt = parse_as_number_or_partial_datetime('2010')
    assert (dt == 2010)


@istest
def parse_as_number_or_datetime_can_parse_float():
    dt = parse_as_number_or_partial_datetime('12.345')
    assert (dt == 12.345)


# Tests for find_last_day_of_month
@istest
def find_last_day_of_month_finds_day_for_dec_2010():
    day = find_last_day_of_month(2010, 12)
    assert (day == 31)


@istest
def find_last_day_of_month_finds_day_for_feb_2000():
    day = find_last_day_of_month(2000, 2)
    assert (day == 29)


# Tests for convert_datetime_components_to_datetime
@istest
def convert_datetime_components_to_datetime_can_convert_year_as_lower_limit():
    dt = convert_datetime_components_to_datetime([2000], True)
    assert (dt == datetime.datetime(2000, 1, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_int_as_lower_limit():
    dt = convert_datetime_components_to_datetime(2000, True)
    assert (dt == datetime.datetime(2000, 1, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_as_upper_limit():
    dt = convert_datetime_components_to_datetime([2000], False)
    assert (dt == datetime.datetime(2000, 12, 31, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_int_as_upper_limit():
    dt = convert_datetime_components_to_datetime(2000, False)
    assert (dt == datetime.datetime(2000, 12, 31, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6], True)
    assert (dt == datetime.datetime(1990, 6, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6], False)
    assert (dt == datetime.datetime(1990, 6, 30, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_day_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7], True)
    assert (dt == datetime.datetime(1990, 6, 7, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_day_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7], False)
    assert (dt == datetime.datetime(1990, 6, 7, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 18], True)
    assert (dt == datetime.datetime(1990, 6, 7, 18, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 18], False)
    assert (dt == datetime.datetime(1990, 6, 7, 18, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 6, 30], True)
    assert (dt == datetime.datetime(1990, 6, 7, 6, 30, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 6, 30], False)
    assert (dt == datetime.datetime(1990, 6, 7, 6, 30, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_sec_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 12, 15, 45], True)
    assert (dt == datetime.datetime(1990, 6, 7, 12, 15, 45))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_sec_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 12, 15, 45], False)
    assert (dt == datetime.datetime(1990, 6, 7, 12, 15, 45))


@istest
@raises(ValueError)
def convert_datetime_components_to_datetime_raises_error_if_invalid_date():
    dt = convert_datetime_components_to_datetime([2000, 6, 31], True)


@istest
@raises(ValueError)
def convert_datetime_components_to_datetime_raises_error_if_invalid_time():
    dt = convert_datetime_components_to_datetime([2000, 6, 30, 12, 30, 60], True)


@istest
def test_that_can_parse_time_deltas():
    delta = parse_datetimestr_delta_to_float_days("P2y15m3dT5M10H3S")
    assert_almost_equal(1190.45829861, delta)


@istest
@raises(ValueError)
def test_that_raise_an_error_when_datetimestr_delta_is_invalid():
    parse_datetimestr_delta_to_float_days("some wierd string")

@istest
def test_that_can_parse_datetimestr_to_obj():
    from cis.time_util import convert_datetime_to_std_time
    import datetime as dt
    # when not specifying the hours, minutes or seconds, 0 is used
    eq_(parse_datetimestr_to_std_time("2010-02-05 02:15:45"),
        convert_datetime_to_std_time(dt.datetime(2010, 2, 5, 2, 15, 45)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02:15"),
        convert_datetime_to_std_time(dt.datetime(2010, 2, 5, 2, 15, 0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02"),
        convert_datetime_to_std_time(dt.datetime(2010, 2, 5, 2, 0, 0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05"),
        convert_datetime_to_std_time(dt.datetime(2010, 2, 5, 0, 0, 0)))

    # GOTCHA: when not specifying an element of a date (i.e. the year, month or day), the current date is used
    now = dt.datetime.now()
    eq_(parse_datetimestr_to_std_time("2010-02-05"),
        convert_datetime_to_std_time(dt.datetime(2010, 2, 5)))
    eq_(parse_datetimestr_to_std_time("2010-12"),
        convert_datetime_to_std_time(dt.datetime(2010, 12, now.day)))
    eq_(parse_datetimestr_to_std_time("2010-"),
        convert_datetime_to_std_time(dt.datetime(2010, now.month, now.day)))


if __name__ == '__main__':
    import nose

    nose.runmodule()
