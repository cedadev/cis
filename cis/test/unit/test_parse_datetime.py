"""Tests for parse_datetime module
"""
from nose.tools import istest, raises, assert_almost_equal, eq_
from cis.parse_datetime import parse_partial_datetime, parse_as_number_or_datetime, parse_datetimestr_delta_to_float_days, \
                               parse_datetimestr_to_std_time
from cis.time_util import PartialDateTime


class MockParserError(Exception):
    pass


class MockParser(object):
    def error(self, message):
        raise MockParserError(message)


# Tests for parse_partial_datetime
@istest
def parse_datetime_can_parse_year():
    parser = MockParser()
    dt = parse_partial_datetime('2010', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010))


@istest
def parse_datetime_can_parse_year_month():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07', 'date/time arg', parser)
    print(dt)
    assert (dt == PartialDateTime(2010, 7))


@istest
def parse_datetime_can_parse_date():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1))


@istest
def parse_datetime_can_parse_date_hour():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01T13', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1, 13))


@istest
def parse_datetime_can_parse_date_hour_min():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01T13:27', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27))


@istest
def parse_datetime_can_parse_date_hour_min_sec():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01T13:27:43', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


@istest
def parse_datetime_can_parse_date_hour_min_sec_no_leading_zeros():
    parser = MockParser()
    dt = parse_partial_datetime('2010-3-4T5:6:7', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 3, 4, 5, 6, 7))


@istest
def parse_datetime_can_parse_date_time_with_space_separator():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01 13:27:43', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


@istest
def parse_datetime_can_parse_date_time_with_colon_separator():
    parser = MockParser()
    dt = parse_partial_datetime('2010-07-01:13:27:43', 'date/time arg', parser)
    assert (dt == PartialDateTime(2010, 7, 1, 13, 27, 43))


@istest
def parse_datetime_passed_error_message_to_parser():
    parser = MockParser()
    name = 'date/time arg'
    try:
        dt = parse_partial_datetime('2X10', name, parser)
    except MockParserError as e:
        assert e.args[0].index(name) > 0


# parse_datetime: Parse errors
@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_character_in_year():
    parser = MockParser()
    dt = parse_partial_datetime('2X10', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_time_but_incomplete_date():
    parser = MockParser()
    dt = parse_partial_datetime('2010-10T12:00', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_too_many_date_components():
    parser = MockParser()
    dt = parse_partial_datetime('2010-10-05-06', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_too_many_time_components():
    parser = MockParser()
    dt = parse_partial_datetime('2010-10-05T12:01:02:03', 'date/time arg', parser)


# parse_datetime: Strings that parse correctly but correspond to invalid date/times
@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_month():
    parser = MockParser()
    dt = parse_partial_datetime('2010-13', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_day():
    parser = MockParser()
    dt = parse_partial_datetime('2010-06-31', 'date/time arg', parser)


# Tests for parse_as_number_or_datetime
@istest
def parse_as_number_or_datetime_can_parse_date_as_datetime():
    from datetime import datetime
    parser = MockParser()
    dt = parse_as_number_or_datetime('2010-07-01', 'date/time arg', parser)
    assert (dt == datetime(2010, 7, 1))


@istest
def parse_as_number_or_datetime_can_parse_integer():
    parser = MockParser()
    dt = parse_as_number_or_datetime('2010', 'limit arg', parser)
    assert (dt == 2010)


@istest
def parse_as_number_or_datetime_can_parse_float():
    parser = MockParser()
    dt = parse_as_number_or_datetime('12.345', 'limit arg', parser)
    assert (dt == 12.345)


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
        convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 0o2, 15, 45)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02:15"),
        convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 0o2, 15, 0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05 02"),
        convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 0o2, 0, 0)))
    eq_(parse_datetimestr_to_std_time("2010-02-05"),
        convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 0, 0, 0)))

    # GOTCHA: when not specifying an element of a date (i.e. the year, month or day), the current date is used
    now = dt.datetime.now()
    eq_(parse_datetimestr_to_std_time("2010-02-05"),
        convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5)))
    eq_(parse_datetimestr_to_std_time("2010-12"),
        convert_datetime_to_std_time(dt.datetime(2010, 12, now.day)))
    eq_(parse_datetimestr_to_std_time("2010-"),
        convert_datetime_to_std_time(dt.datetime(2010, now.month, now.day)))


if __name__ == '__main__':
    import nose

    nose.runmodule()
