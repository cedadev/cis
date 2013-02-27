"""
Utilities for converting time units
"""
import datetime as dt
import numpy as np
from datetime import timedelta

def convert_tai_to_obj_array(tai_time_array):
    for x in np.nditer(tai_time_array, op_flags=['readwrite']):
        x[...] = convert_tai_to_obj(x,dt.datetime(1993,1,1))

def convert_tai_to_obj(tai_time, ref):
    return timedelta(seconds=tai_time) + ref


a = np.arange(6).reshape(2,3)
print a
convert_tai_to_obj_array(a)
print a