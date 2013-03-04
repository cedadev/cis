"""
Utilities for converting time units
"""
import numpy as np

def parse_datetimestr_to_obj(s):
    import dateutil.parser as du
    return du.parse(s)


def parse_datetimestr_to_obj_array(string_time_array):
    return convert_numpy_array(string_time_array, 'O', parse_datetimestr_to_obj)


def parse_datetimestr_delta_to_obj(s):
    """
    parsing "1y2m3d4H5M6S" into a time delta represented as a relativedelta object
    @param s: string to be parsed
    @return: a relativedelta object
    """
    import re
    from datetime import timedelta

    tokens = re.findall('[0-9]*[ymdHMS]',s)
    
    days = hours = minutes = seconds = 0
    for token in tokens:

        val = int(token.replace('','')[:-1])
        if token[-1:] == "y":
            days += val*365
            continue
        elif token[-1:] == "m":
            days += val*30
            continue
        elif token[-1:] == "d":
            days += val
            continue
        elif token[-1:] == "H":
            hours = val
            continue
        elif token[-1:] == "M":
            minutes = val
            continue
        elif token[-1:] == "S":
            seconds = val
            continue
        else:
            raise ValueError("Invalid time delta format")

    return timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)

def convert_time_since_to_datetime(time_array, units):
    from netcdftime import _dateparse
    import datetime
    units, utc_offset, dt = _dateparse(units)
    dt = datetime.datetime(*dt.timetuple()[0:6])
    if units == 'days':
        new_array = convert_numpy_array(time_array, 'O', convert_days_since_to_obj, dt)
    elif units == 'secs':
        new_array = convert_numpy_array(time_array, 'O', convert_sec_since_to_obj, dt)
    return new_array


def convert_tai_to_mpl_array(tai_time_array, ref):
    intermediate_array = convert_numpy_array(tai_time_array, 'O', convert_sec_since_to_obj, ref)
    return convert_numpy_array(intermediate_array, 'int64', convert_datetime_to_num)


def convert_dt_to_mpl(dt):
    import matplotlib.dates as dates
    return dates.date2num(dt)


def convert_sec_since_to_obj_array(tai_time_array, ref):
    return convert_numpy_array(tai_time_array, 'O', convert_sec_since_to_obj, ref)


def convert_sec_since_to_obj(seconds, ref):
    from datetime import timedelta
    return timedelta(seconds=int(seconds)) + ref


def convert_days_since_to_obj(days, ref):
    from datetime import timedelta
    return timedelta(days=float(days)) + ref


def convert_julian_date_to_obj_array(julian_time_array, calender='julian'):
    from iris.unit import julian_day2date
    return convert_numpy_array(julian_time_array, 'O', julian_day2date, calender)


def convert_obj_to_julian_date_array(time_array, calander='julian'):
    from iris.unit import date2julian_day
    return convert_numpy_array(time_array, 'float64', date2julian_day, calander)


def convert_datetime_to_num(dt):
    from iris.unit import encode_time
    return encode_time(*dt.timetuple()[0:6])


def convert_num_to_datetime(time_number):
    from iris.unit import decode_time
    from datetime import datetime
    dt_tuple = decode_time(time_number)
    return datetime(dt_tuple[0], dt_tuple[1], dt_tuple[2], dt_tuple[3], dt_tuple[4], int(dt_tuple[5]))


def convert_datetime_to_num_array(time_array):
    return convert_numpy_array(time_array, 'int64',convert_datetime_to_num)


def convert_num_to_datetime_array(num_array):
    return convert_numpy_array(num_array, 'O', convert_num_to_datetime)


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
    if isinstance(array,np.ma.MaskedArray):
        new_array = convert_masked_array_type(array, new_type, operation, *args, **kwargs)
    else:
        new_array = convert_array_type(array, new_type, operation, *args, **kwargs)
    return new_array
