"""
Utilities for converting time units
"""
import netcdftime
import numpy as np
from iris.unit import Unit

cis_standard_time_unit = Unit('days since 1600-01-01 00:00:00', calendar='gregorian')


def parse_datetimestr_to_std_time(s):
    import dateutil.parser as du
    return cis_standard_time_unit.date2num(du.parse(s))


def parse_datetimestr_to_std_time_array(string_time_array):
    return convert_numpy_array(string_time_array, 'float64', parse_datetimestr_to_std_time)


def parse_datetimestr_delta_to_float_days(s):
    """
    Parses "PY2M3DT4H5M6S" (ISO 8061) into a fractional day
    :param s: string to be parsed
    :return: a float representation of a day
    """
    import re
    from datetime import timedelta

    s = s.upper()

    match = re.match(r'(?:[P])(?P<date>[^T :]+)?(?:[T :])?(?P<time>.+)?$', s)

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

    sec = 1.0/(24.0*60.0*60.0)  # Conversion from sec to day

    days = hours = minutes = seconds = 0
    for token in date_tokens:
        val = int(token[:-1])
        if token[-1:] == "Y":
            days += val*365.2425
        elif token[-1:] == "M":
            days += val*365.2425/12.0
        elif token[-1:] == "D":
            days += val
        else:
            raise ValueError('Date/Time step must be in ISO 8061 format, for example PY2M3DT4H5M6S.')

    for token in time_tokens:
        val = int(token[:-1])
        if token[-1:] == "H":
            hours = val
        elif token[-1:] == "M":
            minutes = val
        elif token[-1:] == "S":
            seconds = val
        else:
            raise ValueError('Date/Time step must be in ISO 8061 format, for example PY2M3DT4H5M6S.')

    print days, hours, minutes, seconds

    td = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return td.total_seconds()*sec


def calculate_mid_time(t1, t2):
    '''
        Find the mid time between two times expressed as floats

    :param t1: a time represented as a float
    :param t2: a time in the same representation as t1
    :return: a float representing the time between t1 and t2
    '''
    return t1 + (t2 - t1)/2.0


def convert_time_since_to_std_time(time_array, units):
    from netcdftime import _dateparse
    import datetime
    units_no_colon_in_since = units.replace("since:", "since")

    units, utc_offset, dt = _dateparse(units_no_colon_in_since)
    dt = datetime.datetime(*dt.timetuple()[0:6])
    if units.lower() == 'days':
        new_array = convert_numpy_array(time_array, 'float64', convert_days_since_to_std_time, dt)
    elif units.lower().startswith('sec'):
        new_array = convert_numpy_array(time_array, 'float64', convert_sec_since_to_std_time, dt)
    else:
        raise NotImplementedError('Tried to convert a time with unrecognised units')
    return new_array


def convert_time_using_time_stamp_info_to_std_time(time_array, units, time_stamp_info=None):
    """
    Convert the time using time stamp info and the first word of the units
    :param time_array: the time array to convert
    :param units: the units of the array (e.g. day or Days from the file time reference 2012-12-12)
    :param time_stamp_info: the time stamp to use for the convertion
    :return: converted data
    """
    units = units.split()
    if len(units) is 0:
        raise ValueError("Units is empty when converting time")

    units_in_since_form = units[0] + " since " + time_stamp_info

    return convert_time_since_to_std_time(time_array, units_in_since_form)


def convert_sec_since_to_std_time_array(tai_time_array, ref):
    return convert_numpy_array(tai_time_array, 'float64', convert_sec_since_to_std_time, ref)


def convert_sec_since_to_std_time(seconds, ref):
    """
    Convert a number of seconds since a given reference datetime to a number of days since our standard time.
    This in principle could avoid the intermediate step converting to a datetime object except we don't know which
    calender the reference is on, e.g. it could be a 360 day calendar

    :param seconds:
    :param ref:
    :return:
    """
    from datetime import timedelta
    return cis_standard_time_unit.date2num(timedelta(seconds=float(seconds)) + ref)


def convert_days_since_to_std_time(days, ref):
    from datetime import timedelta
    return cis_standard_time_unit.date2num(timedelta(days=float(days)) + ref)


def convert_std_time_to_datetime(std_time):
    return cis_standard_time_unit.num2date(std_time)


def convert_datetime_to_std_time(dt):
    return cis_standard_time_unit.date2num(dt)


def convert_julian_date_to_std_time_array(julian_time_array, calender='standard'):
    return convert_numpy_array(julian_time_array, 'float64', convert_julian_date_to_std_time, calender)


def convert_julian_date_to_std_time(julian_date, calender='standard'):
    from iris.unit import julian_day2date
    return cis_standard_time_unit.date2num(julian_day2date(julian_date, calender))


def convert_obj_to_standard_date_array(time_array):
    return convert_numpy_array(time_array, 'float64', convert_datetime_to_std_time)


def convert_masked_array_type(masked_array, new_type, operation, *args, **kwargs):
    from numpy.ma import getmaskarray
    converted_time = np.ma.array(np.zeros(masked_array.shape, dtype=new_type),
                                 mask=masked_array.mask)

    masks = getmaskarray(masked_array)
    for i, val in np.ndenumerate(masked_array):
        if not masks[i]:
            converted_time[i] = operation(val, *args, **kwargs)
    return converted_time


def convert_array_type(array, new_type, operation, *args, **kwargs):
    converted_time = np.zeros(array.shape, dtype=new_type)
    for i, val in np.ndenumerate(array):
        converted_time[i] = operation(val, *args, **kwargs)
    return converted_time


def convert_numpy_array(array, new_type, operation, *args, **kwargs):
    if isinstance(array, np.ma.MaskedArray):
        new_array = convert_masked_array_type(array, new_type, operation, *args, **kwargs)
    else:
        new_array = convert_array_type(array, new_type, operation, *args, **kwargs)
    return new_array


def convert_cube_time_coord_to_standard_time(cube):
    """Converts the time coordinate from the one in the cube to one based on a standard time unit.
    :param cube: cube to modify
    :return: the cube
    """
    # Find the time coordinate.
    t_coord = cube.coord(standard_name='time')
    data_dim = cube.coord_dims(t_coord)
    if len(data_dim) > 0:
        # And remove it from the cube
        cube.remove_coord(t_coord)

        def convert_date(in_date):
            """Converts a date from its initial unit and calendar to cis_standard_time_unit.

            This implementation converts between calendars by maintaining the day number within the
            year across the conversion. If the source calendar has fewer days in a year, there are
            dates in the destination calendar that can never be returned. If the source calendar has
            more days, an error can result.
            :param in_date: date as a number from a reference date set by the coordinate unit
            :return: modified date as a number from the reference date for the standard time unit
            """
            dt = t_coord.units.num2date(in_date)
            year = dt.year
            unit = 'days since {}-01-01 00:00:00'.format(year)
            day_of_year = netcdftime.date2num(dt, unit, calendar=t_coord.units.calendar)
            start_of_year = cis_standard_time_unit.date2num(netcdftime.datetime(year, 1, 1))
            return start_of_year + day_of_year

        new_datetime_nums = convert_numpy_array(t_coord.points, 'float64', convert_date)
        if t_coord.nbounds > 0:
            new_bound_nums = convert_numpy_array(t_coord.bounds, 'float64', convert_date)
            t_coord.bounds = new_bound_nums

        # Create a new time coordinate by copying the old one, but using our new points and units
        new_time_coord = t_coord
        new_time_coord.points = new_datetime_nums
        new_time_coord.units = cis_standard_time_unit

        # And add the new coordinate back into the cube
        cube.add_dim_coord(new_time_coord, data_dim)

    return cube


def convert_cube_time_coord_to_standard_time_assuming_gregorian_calendar(cube):
    """Converts the time coordinate from the one in the cube to one based on a standard time unit.

    This approach assumes that source date is valid as a date in the calendar set for the
    standard time unit (Gregorian) which will not always be true.
    :param cube: cube to modify
    :return: the cube
    """
    # Get the current time coordinate and it's data dimension
    t_coord = cube.coord(standard_name='time')
    data_dim = cube.coord_dims(t_coord)

    # And remove it from the cube
    cube.remove_coord(t_coord)

    # Convert the raw time numbers to our 'standard' time
    new_datetimes = convert_numpy_array(t_coord.points, 'O', t_coord.units.num2date)
    new_datetime_nums = convert_obj_to_standard_date_array(new_datetimes)

    # Create a new time coordinate by copying the old one, but using our new points and units
    new_time_coord = t_coord
    new_time_coord.points = new_datetime_nums
    new_time_coord.units = cis_standard_time_unit

    # And add the new coordinate back into the cube
    cube.add_dim_coord(new_time_coord, data_dim)

    return cube
