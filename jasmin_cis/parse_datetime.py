import datetime
import re


def _parse_datetime(dt_string):
    """Parse a date/time string.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T. 
    @param dt_string: String to parse
    @return: list of datetime components
    @raise ValueError: if the string cannot be parsed as a date/time
    """
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

    # Check that the components are valid (assuming month and/or date is 1 if missing).
    tmp_components = list(dt_components)
    if len(tmp_components) < 3:
        tmp_components.extend([1] * (3 - len(tmp_components)))
    dt = datetime.datetime(*tmp_components)

    return dt_components


def parse_datetime(dt_string, name, parser):
    """Parse a date/time string from the command line, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    @param dt_string: String to parse
    @param name:      A description of the argument used for error messages
    @param parser:    The parser used to report errors
    @return: datetime value
    """
    try:
        dt = _parse_datetime(dt_string)
    except ValueError:
        parser.error("'" + dt_string + "' is not a valid " + name)
        dt = None
    return dt


def parse_as_number_or_datetime(in_string, name, parser):
    """Parse a string as a number from the command line, or if that fails, as a datetime, reporting parse errors.

    The string should be in an ISO 8601 format except that the date and time
    parts may be separated by a space or colon instead of T.
    @param in_string: String to parse
    @param name:      A description of the argument used for error messages
    @param parser:    The parser used to report errors
    @return: int, float or datetime value
    """
    try:
        ret = int(in_string)
    except ValueError:
        try:
            ret = float(in_string)
        except ValueError:
            try:
                ret = _parse_datetime(in_string)
            except ValueError:
                parser.error("'" + in_string + "' is not a valid " + name)
                ret = None
    return ret


def convert_datetime_components_to_datetime(dt_components, is_lower_limit):
    """Converts date and time components: year, month, day, hours, minutes, seconds to a datetime object for use
    as a limit.

    Components beyond the year are defaulted if absent, taking minimum or maximum values if the value of
    is_lower_limit is True or False respectively.
    @param dt_components: list of date/time components as integers in the order:year, month, day, hours, minutes,
        seconds. At least the year must be specified. If only the year is specified it may be passed as an integer.
    @param is_lower_limit: If True, use minimum value for missing date/time components, otherwise use maximum.
    """
    YEAR_INDEX = 0
    DAY_INDEX = 2

    if isinstance(dt_components, list):
        all_components = list(dt_components)
    else:
        all_components = [dt_components]

    if is_lower_limit:
        default_limits = [None, 1, 1, 0, 0, 0]
    else:
        default_limits = [None, 12, None, 23, 59, 59]

    # Fill in the trailing fields with default values.
    for idx in range(len(all_components), len(default_limits)):
        if idx == YEAR_INDEX:
            # Don't default the year - this is the minimum that must be specified.
            pass
        elif idx == DAY_INDEX and not is_lower_limit:
            # Set day to last day of month.
            all_components.append(find_last_day_of_month(*all_components))
        else:
            all_components.append(default_limits[idx])
    return datetime.datetime(*all_components)


def find_last_day_of_month(year, month):
    """Finds the last day of a month.

    @param year: year as integer
    @param month: month as integer
    @return: last day of month as integer
    """
    next_month = datetime.datetime(year, month, 28) + datetime.timedelta(days=4)
    last_date = next_month - datetime.timedelta(days=next_month.day)
    return last_date.day
