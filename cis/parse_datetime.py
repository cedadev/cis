from collections import namedtuple
import datetime
import re
from cis.time_util import cis_standard_time_unit


def parse_datetimestr_to_std_time(s):
    import dateutil.parser as du
    return cis_standard_time_unit.date2num(du.parse(s))


def _parse_actual_datetime(s):
    import dateutil.parser as du
    return du.parse(s)


def _parse_datetime(dt_string):
    # TODO: This only really parses partial datetimes...
    """Parse a date/time string.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    :param dt_string: String to parse
    :return: list of datetime components
    :raise ValueError: if the string cannot be parsed as a date/time
    """
    from cis.time_util import PartialDateTime

    # Separate date and time at first character that is one of 'T', ' ' or ':'.
    match = re.match(r'(?P<date>[^T :]+)(?:[T :])(?P<time>.+)$', dt_string)
    if match is not None:
        date_str = match.group('date')
        time_components = [int(x) for x in match.group('time').split(':')]
    else:
        date_str = dt_string
        time_components = []

    date_components = [int(x) for x in date_str.split('-')]

    dt_components = list(date_components)
    if ((len(date_components) > 3) or (len(time_components) > 3) or
            (len(date_components) < 3) and (len(time_components) > 0)):
        raise ValueError()
    else:
        dt_components.extend(time_components)

    return PartialDateTime(*dt_components)


def parse_datetime(dt_string, name, parser):
    """Parse a date/time string from the command line, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    :param dt_string: String to parse
    :param name:      A description of the argument used for error messages
    :param parser:    The parser used to report errors
    :return: datetime value
    """
    try:
        dt = _parse_datetime(dt_string)
    except ValueError:
        parser.error("'" + dt_string + "' is not a valid " + name)
        dt = None
    return dt


def date_delta_creator(year, month=0, day=0, hour=0, minute=0, second=0):
    date_delta_tuple = namedtuple('date_delta', ['year', 'month', 'day', 'hour', 'minute', 'second'])
    return date_delta_tuple(int(year), int(month), int(day), int(hour), int(minute), int(second))


def _parse_datetime_delta(dt_string):
    """Parse a date/time delta string into years, months, days, hours, minutes and seconds.

    :param dt_string: String to parse, for example 'PY2M3DT4H5M6S' (ISO 8061)
    :return: Named tuple 'date_delta' containing, 'year', 'month', 'day', 'hour', 'minute', 'second'
    :raise ValueError: if the string cannot be parsed as a date/time delta
    """

    dt_string = dt_string.upper()

    match = re.match(r'(?:[P])(?P<date>[^T :]+)?(?:[T :])?(?P<time>.+)?$', dt_string)

    if match is None:
        raise ValueError('Date/Time step must be in ISO 8061 format, for example PY2M3DT4H5M6S.')

    if match.group('date') is not None:
        date_string = match.group('date')
    else:
        date_string = ''

    if match.group('time') is not None:
        time_string = match.group('time')
    else:
        time_string = ''

    date_tokens = re.findall('[0-9]*[A-Z]', date_string)
    time_tokens = re.findall('[0-9]*[A-Z]', time_string)

    years = 0
    months = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    for token in date_tokens:
        val = int(token[:-1])
        if token[-1:] == "Y":
            years = val
        elif token[-1:] == "M":
            months = val
        elif token[-1:] == "D":
            days = val
        else:
            raise ValueError("Date/Time step must be in ISO 8061 format, for example PY2M3DT4H5M6S")

    for token in time_tokens:
        val = int(token[:-1])
        if token[-1:] == "H":
            hours = val
        elif token[-1:] == "M":
            minutes = val
        elif token[-1:] == "S":
            seconds = val
        else:
            raise ValueError("Date/Time step must be in ISO 8061 format, for example PY2M3DT4H5M6S")

    times = [years, months, days, hours, minutes, seconds]

    return date_delta_creator(*times)


def parse_datetime_delta(dt_string, name, parser):
    """Parse a date/time delta string from the command line, reporting parse errors.

    :param dt_string: String to parse
    :param name:      A description of the argument used for error messages
    :param parser:    The parser used to report errors
    :return: timedelta value
    """
    try:
        dt = _parse_datetime_delta(dt_string)
    except ValueError:
        parser.error("'" + dt_string + "' is not a valid " + name)
        dt = None
    return dt


def parse_datetimestr_delta_to_float_days(string):
    """
    Parses "PY2M3DT4H5M6S" (ISO 8061) into a fractional day
    :param string: string to be parsed
    :return: a float representation of a day
    """
    from datetime import timedelta

    date_delta = _parse_datetime_delta(string)

    sec = 1.0/(24.0*60.0*60.0)  # Conversion from sec to day

    days = date_delta.day + date_delta.month*365.2425/12.0 + date_delta.year*365.2425

    td = timedelta(days=days, hours=date_delta.hour, minutes=date_delta.minute, seconds=date_delta.second)

    return td.total_seconds()*sec


def parse_as_number_or_datetime(in_string, name, parser):
    """Parse a string as a number from the command line, or if that fails, as a datetime, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    :param in_string: String to parse
    :param name:      A description of the argument used for error messages
    :param parser:    The parser used to report errors
    :return: int, or float value (possibly converted to the standard time from a time string)
    """
    import dateutil.parser as du
    try:
        ret = int(in_string)
    except ValueError:
        try:
            ret = float(in_string)
        except ValueError:
            try:
                ret = _parse_datetime(in_string)
            except ValueError:
                try:
                    ret = _parse_datetime_delta(in_string)
                except ValueError:
                    parser.error("'" + in_string + "' is not a valid " + name)
                    ret = None
    return ret


def parse_as_float_or_time_delta(arg, name, parser):
    if arg:
        try:
            # First try and parse as a float
            arg = float(arg)
        except ValueError:
            # Then try and parse as a timedelta
            try:
                arg = parse_datetimestr_delta_to_float_days(arg)
            except ValueError:
                # Otherwise throw an error
                parser.error("'" + arg + "' is not a valid " + name)
        return arg
    else:
        return None


