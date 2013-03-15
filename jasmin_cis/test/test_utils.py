from jasmin_cis.utils import apply_intersection_mask_to_two_arrays
from nose.tools import istest, eq_

@istest
def can_apply_intersection_mask_to_two_masked_arrays():
    import numpy.ma as ma
    import numpy as np
    array1 = ma.array([1,2,3,4,5,6,7,8,9,10], mask=[1,1,1,0,0,0,0,0,0,0])
    array2 = ma.array([2,4,5,6,7,8,4,3,6,80], mask=[0,1,0,0,0,0,0,1,0,0])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    assert(np.equal(array1.mask, [1,1,1,0,0,0,0,1,0,0]).all())
    assert(np.equal(array2.mask, [1,1,1,0,0,0,0,1,0,0]).all())

@istest
def can_apply_intersection_mask_to_three_masked_arrays():
    import numpy.ma as ma
    array1 = ma.array([1,2,3,4,5,6,7,8,9,10], mask=[1,1,1,0,0,0,0,0,0,0])
    array2 = ma.array([2,4,5,6,7,8,4,3,6,80], mask=[0,1,0,0,0,0,0,1,0,0])
    array3 = ma.array([2,4,5,6,7,8,4,3,6,80], mask=[0,0,0,0,0,0,0,0,0,1])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    array1, array3 = apply_intersection_mask_to_two_arrays(array1, array3)
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)

    assert(ma.equal(array1.mask, [1,1,1,0,0,0,0,1,0,1]).all())
    assert(ma.equal(array2.mask, [1,1,1,0,0,0,0,1,0,1]).all())
    assert(ma.equal(array3.mask, [1,1,1,0,0,0,0,1,0,1]).all())


@istest
def can_apply_intersection_mask_to_one_masked_and_one_unmasked_array():
    import numpy.ma as ma
    import numpy as np
    array1 = ma.array([1,2,3,4,5,6,7,8,9,10], mask=[1,1,1,0,0,0,0,0,0,0])
    array2 = np.array([2,4,5,6,7,8,4,3,6,80])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    assert(np.equal(array1.mask, [1,1,1,0,0,0,0,0,0,0]).all())
    assert(np.equal(array2.mask,[1,1,1,0,0,0,0,0,0,0]).all())

@istest
def can_apply_intersection_mask_to_two_unmasked_arrays():
    import numpy.ma as ma
    import numpy as np
    array1 = np.array([1,2,3,4,5,6,7,8,9,10])
    array2 = np.array([2,4,5,6,7,8,4,3,6,80])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    assert(array1.mask, False)
    assert(array2.mask, False)

@istest
def can_expand_1d_array_accross():
    import numpy as np
    from jasmin_cis.utils import expand_1d_to_2d_array
    a = np.array([1,2,3,4])
    b = expand_1d_to_2d_array(a, 4, axis=0)
    ref = np.array([[1, 2, 3, 4],[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]])
    assert(np.equal(b, ref).all())

@istest
def can_expand_1d_array_down():
    import numpy as np
    from jasmin_cis.utils import expand_1d_to_2d_array
    a = np.array([1,2,3,4])
    b = expand_1d_to_2d_array(a, 4, axis=1)
    ref = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]])
    assert(np.equal(b, ref).all())
