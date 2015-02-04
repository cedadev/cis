from hamcrest import assert_that, is_
import numpy

def assert_arrays_equal(result, expected):
        assert_that(numpy.array_equal(result, expected), is_(True),
                "arrays not the same. Expected\n {}\n was\n {}".format(expected, result))


def assert_arrays_almost_equal(result, expected):
        assert_that(numpy.allclose(result, expected, atol=1.0e-15)
                    , is_(True),
                    "arrays not almost the same. Expected\n {}\n was\n {}".format(expected, result))


def compare_masked_arrays(a1, a2):
    """
    Compare two masked arrays:
    - Masks should be the same
    - Unmasked data should be same
    - Shape should be same
    - Numeric values that are 'masked out' don't matter
    """
    flat_1 = a1.compressed()
    flat_2 = a2.compressed()
    assert_that(numpy.allclose(flat_1, flat_2), 'Masked arrays have different values')
    assert_that(numpy.array_equal(a1.mask, a2.mask), 'Masked arrays have different masks')
    assert_that(a1.shape, is_(a2.shape), 'Masked arrays have different shapes')