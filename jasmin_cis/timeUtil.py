"""
Utilities for converting time units
"""
import datetime as dt
import numpy as np
from datetime import timedelta

def convert_tai_to_obj_array(tai_time_array,refDate):
    converted_time = np.zeros(tai_time_array.shape, dtype='O')
    for i,t in np.ndenumerate(tai_time_array):
        converted_time[i] = convert_tai_to_obj(int(t),refDate)
    return converted_time

def convert_tai_to_obj(tai_time, refDate):
    return timedelta(seconds=tai_time) + refDate



