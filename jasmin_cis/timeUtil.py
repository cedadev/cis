"""
Utilities for converting time units
"""
import numpy as np


def convert_tai_to_obj_array(tai_time_array,ref):
    return convert_masked_array_type(tai_time_array, 'O', convert_tai_to_obj)


def convert_tai_to_obj(tai_time, ref):
    from datetime import timedelta
    return timedelta(seconds=tai_time) + ref


def convert_julian_date_to_obj_array(julian_time_array, calander='julian'):
    from iris.unit import julian_day2date
    return convert_masked_array_type(julian_time_array, 'O', julian_day2date, calander=calander)


def convert_obj_to_julian_date_array(time_array):
    from iris.unit import date2julian_day
    return convert_masked_array_type(time_array, 'float64', date2julian_day)


def convert_datetime_to_num(dt):
    from iris.unit import encode_time
    return encode_time(*dt.timetuple()[0:6])


def convert_num_to_datetime(time_number):
    from iris.unit import decode_time
    from datetime import datetime
    return datetime(*decode_time(time_number))


def convert_datetime_to_num_array(time_array):
    return convert_masked_array_type(time_array, 'float64',convert_datetime_to_num)


def convert_num_to_datetime_array(num_array):
    return convert_masked_array_type(num_array, 'O', convert_num_to_datetime)


def convert_masked_array_type(masked_array, new_type, operation, **kwargs):
    converted_time = np.ma.array(np.zeros(masked_array.shape, dtype=new_type),
                                 mask=masked_array.mask)
    for i, val in np.ndenumerate(masked_array):
        if not masked_array.mask[i]:
            converted_time[i] = operation(val, **kwargs)
    return converted_time
