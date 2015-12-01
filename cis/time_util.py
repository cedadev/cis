"""
Utilities for converting time units
"""
from utils import convert_numpy_array
from iris.unit import Unit

cis_standard_time_unit = Unit('days since 1600-01-01 00:00:00', calendar='gregorian')


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
    reference DateTime should be on the Gregorian calendar.

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


def convert_julian_date_to_std_time_array(julian_time_array, calender='standard'):
    return convert_numpy_array(julian_time_array, 'float64', convert_julian_date_to_std_time, calender)


def convert_julian_date_to_std_time(julian_date, calender='standard'):
    from iris.unit import julian_day2date
    return cis_standard_time_unit.date2num(julian_day2date(julian_date, calender))


def convert_obj_to_standard_date_array(time_array):
    return convert_numpy_array(time_array, 'float64', convert_datetime_to_std_time)


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
