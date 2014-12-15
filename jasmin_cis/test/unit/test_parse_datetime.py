"""Tests for parse_datetime module
"""
import datetime
from nose.tools import istest, raises
from jasmin_cis.parse_datetime import (parse_datetime, parse_as_number_or_datetime, find_last_day_of_month,
                                       convert_datetime_components_to_datetime)


class MockParserError(Exception):
    pass


class MockParser(object):
    def error(self, message):
        raise MockParserError(message)


# Tests for parse_datetime
@istest
def parse_datetime_can_parse_year():
    parser = MockParser()
    dt = parse_datetime('2010', 'date/time arg', parser)
    assert(dt == [2010])


@istest
def parse_datetime_can_parse_year_month():
    parser = MockParser()
    dt = parse_datetime('2010-07', 'date/time arg', parser)
    print dt
    assert(dt == [2010, 7])


@istest
def parse_datetime_can_parse_date():
    parser = MockParser()
    dt = parse_datetime('2010-07-01', 'date/time arg', parser)
    assert(dt == [2010, 7, 1])


@istest
def parse_datetime_can_parse_date_hour():
    parser = MockParser()
    dt = parse_datetime('2010-07-01T13', 'date/time arg', parser)
    assert(dt == [2010, 7, 1, 13])


@istest
def parse_datetime_can_parse_date_hour_min():
    parser = MockParser()
    dt = parse_datetime('2010-07-01T13:27', 'date/time arg', parser)
    assert(dt == [2010, 7, 1, 13, 27])


@istest
def parse_datetime_can_parse_date_hour_min_sec():
    parser = MockParser()
    dt = parse_datetime('2010-07-01T13:27:43', 'date/time arg', parser)
    assert(dt == [2010, 7, 1, 13, 27, 43])


@istest
def parse_datetime_can_parse_date_hour_min_sec_no_leading_zeros():
    parser = MockParser()
    dt = parse_datetime('2010-3-4T5:6:7', 'date/time arg', parser)
    assert(dt == [2010, 3, 4, 5, 6, 7])


@istest
def parse_datetime_can_parse_date_time_with_space_separator():
    parser = MockParser()
    dt = parse_datetime('2010-07-01 13:27:43', 'date/time arg', parser)
    assert(dt == [2010, 7, 1, 13, 27, 43])


@istest
def parse_datetime_can_parse_date_time_with_colon_separator():
    parser = MockParser()
    dt = parse_datetime('2010-07-01:13:27:43', 'date/time arg', parser)
    assert(dt == [2010, 7, 1, 13, 27, 43])


@istest
def parse_datetime_passed_error_message_to_parser():
    parser = MockParser()
    name = 'date/time arg'
    try:
        dt = parse_datetime('2X10', name, parser)
    except MockParserError as e:
        assert e.message.index(name) > 0


# parse_datetime: Parse errors
@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_character_in_year():
    parser = MockParser()
    dt = parse_datetime('2X10', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_time_but_incomplete_date():
    parser = MockParser()
    dt = parse_datetime('2010-10T12:00', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_too_many_date_components():
    parser = MockParser()
    dt = parse_datetime('2010-10-05-06', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_too_many_time_components():
    parser = MockParser()
    dt = parse_datetime('2010-10-05T12:01:02:03', 'date/time arg', parser)


# parse_datetime: Strings that parse correctly but correspond to invalid date/times
@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_month():
    parser = MockParser()
    dt = parse_datetime('2010-13', 'date/time arg', parser)


@istest
@raises(MockParserError)
def parse_datetime_raises_error_if_invalid_day():
    parser = MockParser()
    dt = parse_datetime('2010-06-31', 'date/time arg', parser)


# Tests for parse_as_number_or_datetime
@istest
def parse_as_number_or_datetime_can_parse_date_as_datetime():
    parser = MockParser()
    dt = parse_as_number_or_datetime('2010-07-01', 'date/time arg', parser)
    assert(dt == [2010, 7, 1])


@istest
def parse_as_number_or_datetime_can_parse_integer():
    parser = MockParser()
    dt = parse_as_number_or_datetime('2010', 'limit arg', parser)
    assert(dt == 2010)


@istest
def parse_as_number_or_datetime_can_parse_float():
    parser = MockParser()
    dt = parse_as_number_or_datetime('12.345', 'limit arg', parser)
    assert(dt == 12.345)


# Tests for find_last_day_of_month
@istest
def find_last_day_of_month_finds_day_for_dec_2010():
    day = find_last_day_of_month(2010, 12)
    assert(day == 31)


@istest
def find_last_day_of_month_finds_day_for_feb_2000():
    day = find_last_day_of_month(2000, 2)
    assert(day == 29)


# Tests for convert_datetime_components_to_datetime
@istest
def convert_datetime_components_to_datetime_can_convert_year_as_lower_limit():
    dt = convert_datetime_components_to_datetime([2000], True)
    assert(dt == datetime.datetime(2000, 1, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_int_as_lower_limit():
    dt = convert_datetime_components_to_datetime(2000, True)
    assert(dt == datetime.datetime(2000, 1, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_as_upper_limit():
    dt = convert_datetime_components_to_datetime([2000], False)
    assert(dt == datetime.datetime(2000, 12, 31, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_int_as_upper_limit():
    dt = convert_datetime_components_to_datetime(2000, False)
    assert(dt == datetime.datetime(2000, 12, 31, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6], True)
    assert(dt == datetime.datetime(1990, 6, 1, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6], False)
    assert(dt == datetime.datetime(1990, 6, 30, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_day_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7], True)
    assert(dt == datetime.datetime(1990, 6, 7, 0, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_year_month_day_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7], False)
    assert(dt == datetime.datetime(1990, 6, 7, 23, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 18], True)
    assert(dt == datetime.datetime(1990, 6, 7, 18, 0, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 18], False)
    assert(dt == datetime.datetime(1990, 6, 7, 18, 59, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 6, 30], True)
    assert(dt == datetime.datetime(1990, 6, 7, 6, 30, 0))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 6, 30], False)
    assert(dt == datetime.datetime(1990, 6, 7, 6, 30, 59))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_sec_as_lower_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 12, 15, 45], True)
    assert(dt == datetime.datetime(1990, 6, 7, 12, 15, 45))


@istest
def convert_datetime_components_to_datetime_can_convert_date_hour_min_sec_as_upper_limit():
    dt = convert_datetime_components_to_datetime([1990, 6, 7, 12, 15, 45], False)
    assert(dt == datetime.datetime(1990, 6, 7, 12, 15, 45))


@istest
@raises(ValueError)
def convert_datetime_components_to_datetime_raises_error_if_invalid_date():
    dt = convert_datetime_components_to_datetime([2000, 6, 31], True)


@istest
@raises(ValueError)
def convert_datetime_components_to_datetime_raises_error_if_invalid_time():
    dt = convert_datetime_components_to_datetime([2000, 6, 30, 12, 30, 60], True)


if __name__ == '__main__':
    import nose
    nose.runmodule()
