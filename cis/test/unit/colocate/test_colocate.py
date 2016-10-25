"""
Tests the cis.col.Collocate class
"""
import unittest
from nose.tools import assert_raises


class TestCollocate(unittest.TestCase):
    def test_get_kernel(self):
        from cis.collocation.col_implementations import moments, nn_pressure, mean
        from cis.collocation.col import get_kernel

        assert isinstance(get_kernel('moments'), moments)
        assert isinstance(get_kernel(nn_pressure()), nn_pressure)
        assert isinstance(get_kernel('mean', default=moments), mean)
        assert isinstance(get_kernel('', default=moments), moments)

        with assert_raises(ValueError):
            get_kernel('foo')

        with assert_raises(ValueError):
            get_kernel('foo', default=moments)