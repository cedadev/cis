'''
Utility functions used by both hdf_sd and hdf_vd
'''
import numpy as np

def __fill_missing_data(data, missing_val):
    import numpy.ma as ma
    #w_fill_mask = np.where(data == missing_val, np.nan, 1)
    #temp = data * w_fill_mask
    return ma.array(data,mask=data==missing_val) 