"""
Utilities for converting time units
"""
import numpy as np

def convert_tai_to_obj_array(tai_time_array,refDate):
    converted_time = np.zeros(tai_time_array.shape, dtype='O')
    for i,t in np.ndenumerate(tai_time_array):
        converted_time[i] = convert_tai_to_obj(int(t),refDate)
    return converted_time

def convert_tai_to_obj(tai_time, refDate):
    from datetime import timedelta
    return timedelta(seconds=tai_time) + refDate

def convert_julian_date_to_obj_array(julian_time_array, calander):
    from iris.unit import julian_day2date

    converted_time = np.ma.array(np.zeros(julian_time_array.shape, dtype='O'),
                                 mask=julian_time_array.mask)
    for i, t in np.ndenumerate(julian_time_array):
        if not julian_time_array.mask[i]:
            converted_time[i] = julian_day2date(t, calander)
    return converted_time

def convert_obj_to_julian_date_array(time_array):
    from iris.unit import date2julian_day

    converted_time = np.ma.array(np.zeros(time_array.shape, dtype='float64'),
                                 mask=time_array.mask)
    for i, t in np.ndenumerate(time_array):
        if not time_array.mask[i]:
            converted_time[i] = date2julian_day(t, 'julian')
    return converted_time

def convert_datetime_to_num_array(time_array):
    from iris.unit import encode_time

    converted_time = np.ma.array(np.zeros(time_array.shape, dtype='float64'),
                                 mask=time_array.mask)
    for i, date_time in np.ndenumerate(time_array):
        if not time_array.mask[i]:
            converted_time[i] = encode_time(*date_time.timetuple()[0:6])
    return converted_time

def convert_num_to_datetime_array(self):
    from iris.unit import decode_time
    from datetime import datetime
    new_data = np.zeros(self.shape, dtype='O')
    for i, date_time in np.ndenumerate(self.data):
        new_data[i] = decode_time(datetime(*date_time))
    self._data = new_data


def convert_masked_array_type(masked_array, new_type, operation):
    converted_time = np.ma.array(np.zeros(masked_array.shape, dtype=new_type),
                                 mask=masked_array.mask)
    for i, val in np.ndenumerate(masked_array):
        if not masked_array.mask[i]:
            converted_time[i] = operation(val)
    return converted_time
