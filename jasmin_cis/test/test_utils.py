from jasmin_cis.utils import apply_intersection_mask_to_two_arrays, calculate_histogram_bin_edges
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
    import numpy as np
    array1 = np.array([1,2,3,4,5,6,7,8,9,10])
    array2 = np.array([2,4,5,6,7,8,4,3,6,80])
    array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
    assert(all(array1.mask)== False)
    assert(all(array2.mask)== False)

@istest
def can_expand_1d_array_across():
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

@istest
def ten_bins_are_created_by_default():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {}
    step = None

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 11) # 11 edges = 10 bins
    eq_(bin_edges.min(), data.min())
    assert(abs(bin_edges.max() - data.max()) < 1.e-7)

@istest
def bin_width_can_be_specified_where_bin_width_perfectly_divides_range():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {}
    step = 0.5

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 7)
    eq_(bin_edges.min(), data.min())
    eq_(bin_edges.max(), data.max())

@istest
def bin_width_can_be_specified_where_bin_width_does_not_perfectly_divides_range():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {}
    step = 0.7

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 5)
    eq_(bin_edges.min(), data.min())
    assert(bin_edges.max() < data.max())

@istest
def ten_bins_are_created_when_min_is_specified():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {"xmin" : 0.3}
    step = None

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 11) # 11 edges = 10 bins
    eq_(bin_edges.min(), 0.3)
    assert(abs(bin_edges.max() - data.max()) < 1.e-7) # 1.e-7 is approx 0

@istest
def ten_bins_are_created_when_max_is_specified():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {"xmax" : 2.3}
    step = None

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 11) # 11 edges = 10 bins
    eq_(bin_edges.min(), data.min())
    assert(abs(bin_edges.max() - 2.3) < 1.e-7) # 1.e-7 is approx 0'''

@istest
def ten_bins_are_created_when_min_and_max_is_specified():
    from numpy import array
    data = array([0.0, 1.0, 2.0, 3.0])
    val_range = {"xmin" : 0.3, "xmax" : 2.3}
    step = None

    bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
    eq_(len(bin_edges), 11) # 11 edges = 10 bins
    assert(abs(bin_edges.min() - 0.3) < 1.e-7) # 1.e-7 is approx 0
    assert(abs(bin_edges.max() - 2.3) < 1.e-7) # 1.e-7 is approx 0
