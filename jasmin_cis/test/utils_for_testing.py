from hamcrest import assert_that, is_
import numpy

def assert_arrays_equal(result, expected):
        assert_that(numpy.array_equal(result, expected), is_(True),
                "arrays not the same. Expected\n {}\n was\n {}".format(expected, result))


def assert_arrays_almost_equal(result, expected):
        assert_that(numpy.allclose(result, expected, atol=1.0e-15)
                    , is_(True),
                    "arrays not almost the same. Expected\n {}\n was\n {}".format(expected, result))