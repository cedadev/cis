import unittest

from cis.collocation.col_framework import get_kernel
from cis.test.util import mock
from cis.test.utils_for_testing import *


class TestMomentsKernel(unittest.TestCase):

    def test_GIVEN_ungridded_data_WHEN_collapse_THEN_calculations_correct(self):
        grid = {'y': slice(-12.5, 12.5, 12.5)}
        data = mock.make_regular_2d_ungridded_data()
        kernel_class = get_kernel('moments')
        kernel = kernel_class()
        result = data.aggregate(how=kernel, **grid)

        expected_means = numpy.array([3.5, 11])
        expected_std_dev = numpy.array([numpy.sqrt(3.5), numpy.sqrt(7.5)])
        expected_no = numpy.array([6, 9])
        assert_that(len(result), is_(3))
        assert_arrays_almost_equal(result[0].data.flatten(), expected_means)
        assert_arrays_almost_equal(result[1].data.flatten(), expected_std_dev)
        assert_that(numpy.array_equal(result[2].data.flatten(), expected_no))

    def test_GIVEN_ungridded_data_WHEN_collapse_THEN_metadata_correct(self):
        grid = {'y': slice(-10, 10, 10)}
        data = mock.make_regular_2d_ungridded_data()
        kernel_class = get_kernel('moments')
        kernel = kernel_class()
        result = data.aggregate(how=kernel, **grid)

        mean, stddev, num = result
        assert_that(mean.standard_name, is_('rainfall_rate'))
        assert_that(stddev.standard_name, is_(None))
        assert_that(num.standard_name, is_(None))
        assert_that(mean.long_name, is_('TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(stddev.long_name,
                    is_('Corrected sample standard deviation of TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(num.long_name, is_('Number of points used to calculate the mean of '
                                       'TOTAL RAINFALL RATE: LS+CONV KG/M2/S'))
        assert_that(mean.var_name, is_('rain'))
        assert_that(stddev.var_name, is_('rain_std_dev'))
        assert_that(num.var_name, is_('rain_num_points'))
        assert_that(mean.units, is_('kg m-2 s-1'))
        assert_that(stddev.units, is_('kg m-2 s-1'))
        assert_that(num.units, is_(None))


if __name__ == '__main__':
    unittest.main()
