"""
Utilities for converting time units
"""
import numpy as np

def convert_tai_to_obj_array(tai_time_array,ref):
    converted_time = np.zeros(tai_time_array.shape, dtype='O')
    for i,t in np.ndenumerate(tai_time_array):
        converted_time[i] = convert_tai_to_obj(int(t),ref)
    return converted_time

def convert_tai_to_obj(tai_time, ref):
    from datetime import timedelta
    return timedelta(seconds=tai_time) + ref

def convert_julian_date_to_obj_array(julian_time_array, calander):
    from iris.unit import julian_day2date

    converted_time = np.zeros(julian_time_array.shape, dtype='O')
    for i,t in np.ndenumerate(julian_time_array):
        converted_time[i] = julian_day2date(t, calander)
    return converted_time




# a = np.arange(6).reshape(2,3)
# print a
# b= convert_tai_to_obj_array(a,dt.datetime(1993,1,1))
# print b