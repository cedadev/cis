from jasmin_cis.utils import apply_intersection_mask_to_two_arrays
from nose.tools import istest, eq_

@istest
def can_apply_intersection_mask_to_two_array():
    import numpy.ma as ma
    array1 = ma.array([1,2,3,4,5,6,7,8,9,10], mask=[1,1,1,0,0,0,0,0,0,0])
    array2 = ma.array([2,4,5,6,7,8,4,3,6,80], mask=[0,1,0,0,0,0,0,0,0,0])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    eq_(array1.all(), ma.array([1,2,3,4,5,6,7,8,9,10], mask=[1,1,1,0,0,0,0,0,0,0]).all())
    eq_(array2.all(), ma.array([2,4,5,6,7,8,4,3,6,80], mask=[1,1,1,0,0,0,0,0,0,0]).all())