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

        :param int year:
        :param int month:
        :param int day:
        :param int hour:
        :param int minute:
        :param int second:
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        self.attributes = ['year', 'month', 'day', 'hour', 'minute', 'second']

        # Check we have valid components - there should be no non-None values after the first one (if there is one)
        components = [getattr(self, a) for a in self.attributes]
        if None in components and any(c is not None for c in components[components.index(None):]):
            raise ValueError("All intermediate values must be specified when creating a PartialDateTime")

        # Check that the components are valid by trying to find the minimum date
        try:
            _ = self.min()
        except TypeError:
            raise ValueError("Invalid PartialDateTime arguments")

    def range(self):
        """
        Return the datetime representing the start of the range defined by this object, and that representing the end.

        For example, to create a datetime range for the year 2008:

        >>> from cis.time_util import PartialDateTime
        >>> pdt = PartialDateTime(2008)
        >>> pdt.range()
        datetime(2008,1,1,1,1,1), datetime(2008,12,31,23,59,59)

        Or for February 2001:

        >>> pdt = PartialDateTime(2001, 2)
        >>> pdt.range()
        datetime(2001,2,1,1,1,1), datetime(2008,2,28,23,59,59)

        :return (datetime.datetime, datetime.datetime) : A pair of datetime objects
        """
        return self.min(), self.max()

    def min(self):
        """
        Return the datetime object for the start of the PartialDateTime period. I.e. the earliest valid datetime

        :return datetime.datetime: The earliest datetime
        """
        from datetime import datetime
        lower_limits = [None, 1, 1, 0, 0, 0]

        # Get the initialized date-components
        dt_start = [getattr(self, a) for a in self.attributes if getattr(self, a) is not None]

        # Fill in the remaining fields with default values.
        for idx in range(len(dt_start), len(self.attributes)):
            if self.attributes[idx] == 'day':
                dt_start.append(lower_limits[idx])
            else:
                dt_start.append(lower_limits[idx])
        return datetime(*dt_start)

    def max(self):
        """
        Return the datetime object for the end of the PartialDateTime period. I.e. the latest valid datetime

        :return datetime.datetime: The latest datetime
        """
        from datetime import datetime
        upper_limits = [None, 12, None, 23, 59, 59]

        # Get the initialized date-components
        dt_end = [getattr(self, a) for a in self.attributes if getattr(self, a) is not None]

        # Fill in the remaining fields with default values.
        for idx in range(len(dt_end), len(self.attributes)):
            if self.attributes[idx] == 'day':
                # Set day to last day of month. The year and month will already be in there.
                dt_end.append(find_last_day_of_month(*dt_end))
            else:
                dt_end.append(upper_limits[idx])

        return datetime(*dt_end)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
    """
    Go via datetimes to be on the safe side.
    :param ndaray time_array:
    :param cf_units.Unit units:
    :return:
    """
    dt = units.num2date(time_array)
    return cis_standard_time_unit.date2num(dt)


def convert_time_using_time_stamp_info_to_std_time(time_array, units, time_stamp_info=None):
    """
    Convert the time using time stamp info and the first word of the units
    :param time_array: the time array to convert
    :param str units: the units of the array (e.g. day or Days from the file time reference 2012-12-12)
    :param str time_stamp_info: the time stamp to use for the convertion
    :return: converted data
    """
    from cf_units import Unit
    units = str(units).split()
    if len(units) == 0:
        raise ValueError("Units is empty when converting time")

    units_in_since_form = Unit(units[0] + " since " + time_stamp_info)

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
    days_since = seconds.astype(float, **kwargs) / (3600*24.0)
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
    offset = cis_standard_time_unit.num2date(0).toordinal(fractional=True)
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


def set_year(datetime, new_year):
    """
    Change the year of a datetime to some new year. If datetime is a leapday then return None
    :param datetime.datetime datetime: Datetime object to change
    :param int new_year: The new year
    :return: A datetime with the same date as the original except the changed year
    """
    # Once we have the data as datetimes we can just use replace to change the year...
    try:
        new_dt = datetime.replace(year=new_year)
    except ValueError:
        # ...Unless the date is 29th of Feb!
        new_dt = None
    return new_dt


def change_year_of_ungridded_data(data, new_year):
    """
     This slightly roundabout method works fine, but isn't particularly quick.
      I could just add the number of years times 365, but that does't take leap years into account. If I want to take
      leap years into account I can't use fractional days which would break the time. In principle I could take calculate
      the exact difference in integer days between the first date and the first date in the new year then apply that
      scaling - but THAT won't work if the data set spans a leap day...
    :param data: An ungridded data object to update in-place
    :param int new_year: The year to change the data to
    """
    import numpy as np

    dates = data.coord('time').data

    dt = convert_std_time_to_datetime(dates)

    np_set_year = np.vectorize(set_year)

    updated_dt = np_set_year(dt, new_year)
    new_dates = convert_datetime_to_std_time(updated_dt)

    data.coord('time').data = new_dates
