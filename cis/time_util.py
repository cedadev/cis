"""
Utilities for converting time units
"""
from cf_units import Unit

cis_standard_time_unit = Unit('days since 1600-01-01 00:00:00', calendar='gregorian')


class PartialDateTime(object):
    """
    A :class:`PartialDateTime` object specifies values for some subset of
    the calendar/time fields (year, month, hour, etc.) and defines a period of time,
    primarily for creating ranges of :class:`datetime.datetime` instances.
    """

    def __init__(self, year, month=None, day=None, hour=None, minute=None, second=None):
        """
        Allows creation of datetime ranges. The year is mandatory, all others are optional - but intermediate components
        must be specified. E.g. you can't specify a year and a day with no month.

        Args:

        * year (int):
        * month (int):
        * day (int):
        * hour (int):
        * minute (int):
        * second (int):
        * microsecond (int):

        """
        #: The year number as an integer, or None.
        self.year = year
        #: The month number as an integer, or None.
        self.month = month
        #: The day number as an integer, or None.
        self.day = day
        #: The hour number as an integer, or None.
        self.hour = hour
        #: The minute number as an integer, or None.
        self.minute = minute
        #: The second number as an integer, or None.
        self.second = second

    def convert_to_datetime_range(self):
        """
        Return the datetime representing the start of the range defined by this object, and that representing the end.

        For example, to create a datetime range for the year 2008:

        >>> from cis.time_util import PartialDateTime
        >>> pdt = PartialDateTime(2008)
        >>> pdt.convert_to_datetime_range()
        datetime(2008,1,1,1,1,1), datetime(2008,12,31,23,59,59)

        Or for February 2001:

        >>> pdt = PartialDateTime(2001, 2)
        >>> pdt.convert_to_datetime_range()
        datetime(2001,2,1,1,1,1), datetime(2008,2,28,23,59,59)

        :return (datetime.datetime, datetime.datetime) : A pair of datetime objects
        """
        from datetime import datetime

        attributes = ['year', 'month', 'day', 'hour', 'minute', 'second']
        lower_limits = [None, 1, 1, 0, 0, 0]
        upper_limits = [None, 12, None, 23, 59, 59]

        # Get the initialized date-components
        dt_start = [getattr(self, a) for a in attributes if getattr(self, a) is not None]
        dt_end = [getattr(self, a) for a in attributes if getattr(self, a) is not None]

        # Fill in the remaining fields with default values.
        for idx in range(len(dt_start), len(attributes)):
            if attributes[idx] == 'day':
                dt_start.append(lower_limits[idx])
                # Set day to last day of month. The year and month will already be in there.
                dt_end.append(find_last_day_of_month(*dt_end))
            else:
                dt_start.append(lower_limits[idx])
                dt_end.append(upper_limits[idx])

        return datetime(*dt_start), datetime(*dt_end)


def find_last_day_of_month(year, month):
    """Finds the last day of a month.

    :param year: year as integer
    :param month: month as integer
    :return: last day of month as integer
    """
    import datetime
    next_month = datetime.datetime(year, month, 28) + datetime.timedelta(days=4)
    last_date = next_month - datetime.timedelta(days=next_month.day)
    return last_date.day


def calculate_mid_time(t1, t2):
    """
        Find the mid time between two times expressed as floats

    :param t1: a time represented as a float
    :param t2: a time in the same representation as t1
    :return: a float representing the time between t1 and t2
    """
    return t1 + (t2 - t1)/2.0


def convert_time_since_to_std_time(time_array, units):
    # Strip out any extra colons and commas
    old_time = Unit(units.replace("since:", "since").replace(",", ""))
    dt = old_time.num2date(time_array)
    return cis_standard_time_unit.date2num(dt)


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


def convert_sec_since_to_std_time(seconds, ref):
    """
    Convert a number of seconds since a given reference datetime to a number of days since our standard time. The given
    reference DateTime must be on the Gregorian calendar.

    :param seconds: Array of seconds (since the reference time provided)
    :type: ndarray
    :param ref: The reference datetime which the seconds are counted from
    :type: DateTime
    :return: A numpy array containing all of the time values (in fractional days since the CIS standard time)
    """
    import numpy as np
    # Don't copy the array if this is a standard numpy array, unfortunately masked arrays don't have this option
    kwargs = {} if isinstance(seconds, np.ma.MaskedArray) else {'copy': False}
    days_since = seconds.astype('float64', **kwargs) / (3600*24.0)
    offset = ref - cis_standard_time_unit.num2date(0)
    return offset.days + days_since


def convert_std_time_to_datetime(std_time):
    return cis_standard_time_unit.num2date(std_time)


def convert_datetime_to_std_time(dt):
    return cis_standard_time_unit.date2num(dt)


def convert_julian_date_to_std_time(days_since):
    """
    Convert an array of julian days to cis standard time

    ..note:
        Array should have units like: Julian Date, days elapsed since 12:00 January 1, 4713 BC

    :param days_since: numpy array of fractional days since 12:00 January 1, 4713 BC
    :return: fractional days since cis standard time
    """
    from cf_units import date2julian_day
    offset = date2julian_day(cis_standard_time_unit.num2date(0), 'standard')
    return days_since - offset


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

        dt_points = t_coord.units.num2date(t_coord.points)
        new_datetime_nums = cis_standard_time_unit.date2num(dt_points)

        # new_datetime_nums = convert_numpy_array(t_coord.points, 'float64', convert_date)
        if t_coord.nbounds > 0:
            dt_bounds = t_coord.units.num2date(t_coord.bounds)
            new_bound_nums = cis_standard_time_unit.date2num(dt_bounds)
            t_coord.bounds = new_bound_nums

        # Create a new time coordinate by copying the old one, but using our new points and units
        new_time_coord = t_coord
        new_time_coord.points = new_datetime_nums
        new_time_coord.units = cis_standard_time_unit

        # And add the new coordinate back into the cube
        cube.add_dim_coord(new_time_coord, data_dim)

    return cube
