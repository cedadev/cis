'''
Utility functions used by both hdf_sd and hdf_vd
'''
import numpy as np

def __fill_missing_data(data, missing_val):
    w_fill_mask = np.where(data == missing_val, np.nan, 1)
    return data * w_fill_mask