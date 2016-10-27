import re
from cis.time_util import cis_standard_time_unit
import argparse


def parse_datetimestr_to_std_time(s):
    import dateutil.parser as du
    return cis_standard_time_unit.date2num(du.parse(s))


def _parse_datetime(s):
    """Parse a date/time string.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    """
    import dateutil.parser as du
    return du.parse(s)


def _parse_partial_datetime(dt_string):
    """Parse a partial date/time string.

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


def parse_partial_datetime(dt_string, name, parser):
    """Parse a partial date/time string from the command line, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    :param dt_string: String to parse
    :param name:      A description of the argument used for error messages
    :param parser:    The parser used to report errors
    :return: datetime value
    """
    if dt_string == 'None' or dt_string is None:
        return None
    try:
        dt = _parse_partial_datetime(dt_string)
    except ValueError:
        parser.error("'" + dt_string + "' is not a valid " + name)
        dt = None
    return dt


def parse_datetime(dt_string, name, parser):
    """Parse a date/time string from the command line, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    :param dt_string: String to parse
    :param name:      A description of the argument used for error messages
    :param parser:    The parser used to report errors
    :return: datetime value
    """
    if dt_string == 'None' or dt_string is None:
        return None
    try:
        dt = _parse_datetime(dt_string)
    except ValueError:
        parser.error("'" + dt_string + "' is not a valid " + name)
        dt = None
    return dt


def _parse_datetime_delta(dt_string):
    """Parse a date/time delta string into years, months, days, hours, minutes and seconds.

    :param dt_string: String to parse, for example 'PY2M3DT4H5M6S' (ISO 8601)
    :return: Named tuple 'date_delta' containing, 'year', 'month', 'day', 'hour', 'minute', 'second'
    :raise ValueError: if the string cannot be parsed as a date/time delta
    """
    from datetime import timedelta
    dt_string = dt_string.upper()

    match = re.match(r'(?:[P])(?P<date>[^T :]+)?(?:[T :])?(?P<time>.+)?$', dt_string)

    if match is None:
        raise ValueError('Date/Time step must be in ISO 8601 format, for example PY2M3DT4H5M6S.')

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
            raise ValueError("Date/Time step must be in ISO 8601 format, for example PY2M3DT4H5M6S")

    for token in time_tokens:
        val = int(token[:-1])
        if token[-1:] == "H":
            hours = val
        elif token[-1:] == "M":
            minutes = val
        elif token[-1:] == "S":
            seconds = val
        else:
            raise ValueError("Date/Time step must be in ISO 8601 format, for example PY2M3DT4H5M6S")

    # Note that there is a loss of precision here because we have to convert months and years to integer days
    dt = timedelta(seconds=seconds, minutes=minutes, hours=hours, days=(days + months*30 + years*365))
    return dt


def _datetime_delta_to_float_days(td):
    """
    Converts a timedelta into a fractional day
    :param td: the timedelta to be converted
    :return: a float representation of a day
    """
    sec = 1.0/(24.0*60.0*60.0)  # Conversion from sec to day
    return td.total_seconds()*sec


def parse_datetimestr_delta_to_float_days(string):
    """
    Parses "PY2M3DT4H5M6S" (ISO 8601) into a fractional day
    :param string: string to be parsed
    :return: a float representation of a day
    """

    date_delta = _parse_datetime_delta(string)
    return _datetime_delta_to_float_days(date_delta)


def parse_as_number_or_datetime(string):
    """
    Parse a string as a number from the command line, or if that fails, as a datetime

    :param in_string: String to parse
    :return: int, float or DateTime
    """
    if string == 'None' or string is None:
        return None
    try:
        ret = int(string)
    except ValueError:
        try:
            ret = float(string)
        except ValueError:
            try:
                ret = _parse_datetime(string)
            except ValueError:
                raise argparse.ArgumentTypeError("'{}' is not a valid value.".format(string))
    return ret


def parse_as_number_or_standard_time(string):
    """
    Parse a string as a number from the command line, or if that fails, as a datetime in standard cis units

    :param in_string: String to parse
    :return: int, float (possibly representing a time in CIS standard time units)
    """
    from datetime import datetime
    res = parse_as_number_or_datetime(string)
    if isinstance(res, datetime):
        res = cis_standard_time_unit.date2num(res)
    return res


def parse_as_number_or_datetime_delta(string):
    """
    Parse a string as a number from the command line, or if that fails, as a datetime delta

    :param in_string: String to parse
    :return: int, float value or datetimedelta
    """
    try:
        ret = int(string)
    except ValueError:
        try:
            ret = float(string)
        except ValueError:
            try:
                ret = _parse_datetime_delta(string)
            except ValueError:
                raise argparse.ArgumentTypeError("'{}' is not a valid value.".format(string))
    return ret


