# The TestRegularGridInterpolator class was adapted from the SciPy original here:
# https://github.com/scipy/scipy/blob/master/scipy/interpolate/tests/test_interpolate.py

# Copyright © 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright © 2003-2013 SciPy Developers.
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# No changes were made to the below - they are used to ensure our changes didn't break anything!

from __future__ import division, print_function, absolute_import

import itertools
import numpy as np
from numpy.testing import (assert_array_almost_equal, assert_raises,
                           TestCase, assert_allclose)

from cis.collocation.gridded_interpolation import RegularGridInterpolator
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator


class TestRegularGridInterpolator(TestCase):
    def _get_sample_4d(self):
        # create a 4d grid of 3 points in each dimension
        points = [(0., .5, 1.)] * 4
        values = np.asarray([0., .5, 1.])
        values0 = values[:, np.newaxis, np.newaxis, np.newaxis]
        values1 = values[np.newaxis, :, np.newaxis, np.newaxis]
        values2 = values[np.newaxis, np.newaxis, :, np.newaxis]
        values3 = values[np.newaxis, np.newaxis, np.newaxis, :]
        values = (values0 + values1 * 10 + values2 * 100 + values3 * 1000)
        return points, values

    def _get_sample_4d_2(self):
        # create another 4d grid of 3 points in each dimension
        points = [(0., .5, 1.)] * 2 + [(0., 5., 10.)] * 2
        values = np.asarray([0., .5, 1.])
        values0 = values[:, np.newaxis, np.newaxis, np.newaxis]
        values1 = values[np.newaxis, :, np.newaxis, np.newaxis]
        values2 = values[np.newaxis, np.newaxis, :, np.newaxis]
        values3 = values[np.newaxis, np.newaxis, np.newaxis, :]
        values = (values0 + values1 * 10 + values2 * 100 + values3 * 1000)
        return points, values

    def test_list_input(self):
        points, values = self._get_sample_4d()

        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])

        for method in ['linear', 'nearest']:
            interp = RegularGridInterpolator(points,
                                             values.tolist(),
                                             method=method)
            v1 = interp(sample.tolist())
            interp = RegularGridInterpolator(points,
                                             values,
                                             method=method)
            v2 = interp(sample)
            assert_allclose(v1, v2)

    def test_complex(self):
        points, values = self._get_sample_4d()
        values = values - 2j*values
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])

        for method in ['linear', 'nearest']:
            interp = RegularGridInterpolator(points, values,
                                             method=method)
            rinterp = RegularGridInterpolator(points, values.real,
                                              method=method)
            iinterp = RegularGridInterpolator(points, values.imag,
                                              method=method)

            v1 = interp(sample)
            v2 = rinterp(sample) + 1j*iinterp(sample)
            assert_allclose(v1, v2)

    def test_linear_xi1d(self):
        points, values = self._get_sample_4d_2()
        interp = RegularGridInterpolator(points, values)
        sample = np.asarray([0.1, 0.1, 10., 9.])
        wanted = 1001.1
        assert_array_almost_equal(interp(sample), wanted)

    def test_linear_xi3d(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values)
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        wanted = np.asarray([1001.1, 846.2, 555.5])
        assert_array_almost_equal(interp(sample), wanted)

    def test_nearest(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values, method="nearest")
        sample = np.asarray([0.1, 0.1, .9, .9])
        wanted = 1100.
        assert_array_almost_equal(interp(sample), wanted)
        sample = np.asarray([0.1, 0.1, 0.1, 0.1])
        wanted = 0.
        assert_array_almost_equal(interp(sample), wanted)
        sample = np.asarray([0., 0., 0., 0.])
        wanted = 0.
        assert_array_almost_equal(interp(sample), wanted)
        sample = np.asarray([1., 1., 1., 1.])
        wanted = 1111.
        assert_array_almost_equal(interp(sample), wanted)
        sample = np.asarray([0.1, 0.4, 0.6, 0.9])
        wanted = 1055.
        assert_array_almost_equal(interp(sample), wanted)

    def test_linear_edges(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values)
        sample = np.asarray([[0., 0., 0., 0.], [1., 1., 1., 1.]])
        wanted = np.asarray([0., 1111.])
        assert_array_almost_equal(interp(sample), wanted)

    def test_valid_create(self):
        # create a 2d grid of 3 points in each dimension
        points = [(0., .5, 1.), (0., 1., .5)]
        values = np.asarray([0., .5, 1.])
        values0 = values[:, np.newaxis]
        values1 = values[np.newaxis, :]
        values = (values0 + values1 * 10)
        assert_raises(ValueError, RegularGridInterpolator, points, values)
        points = [((0., .5, 1.), ), (0., .5, 1.)]
        assert_raises(ValueError, RegularGridInterpolator, points, values)
        points = [(0., .5, .75, 1.), (0., .5, 1.)]
        assert_raises(ValueError, RegularGridInterpolator, points, values)
        points = [(0., .5, 1.), (0., .5, 1.), (0., .5, 1.)]
        assert_raises(ValueError, RegularGridInterpolator, points, values)
        points = [(0., .5, 1.), (0., .5, 1.)]
        assert_raises(ValueError, RegularGridInterpolator, points, values,
                      method="undefmethod")

    def test_valid_call(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values)
        sample = np.asarray([[0., 0., 0., 0.], [1., 1., 1., 1.]])
        assert_raises(ValueError, interp, sample, "undefmethod")
        sample = np.asarray([[0., 0., 0.], [1., 1., 1.]])
        assert_raises(ValueError, interp, sample)
        sample = np.asarray([[0., 0., 0., 0.], [1., 1., 1., 1.1]])
        assert_raises(ValueError, interp, sample)

    def test_out_of_bounds_extrap(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values, bounds_error=False,
                                         fill_value=None)
        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [21, 2.1, -1.1, -11], [2.1, 2.1, -1.1, -1.1]])
        wanted = np.asarray([0., 1111., 11., 11.])
        assert_array_almost_equal(interp(sample, method="nearest"), wanted)
        wanted = np.asarray([-111.1, 1222.1, -11068., -1186.9])
        assert_array_almost_equal(interp(sample, method="linear"), wanted)

    def test_out_of_bounds_extrap2(self):
        points, values = self._get_sample_4d_2()
        interp = RegularGridInterpolator(points, values, bounds_error=False,
                                         fill_value=None)
        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [21, 2.1, -1.1, -11], [2.1, 2.1, -1.1, -1.1]])
        wanted = np.asarray([0., 11., 11., 11.])
        assert_array_almost_equal(interp(sample, method="nearest"), wanted)
        wanted = np.asarray([-12.1, 133.1, -1069., -97.9])
        assert_array_almost_equal(interp(sample, method="linear"), wanted)

    def test_out_of_bounds_fill(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values, bounds_error=False,
                                         fill_value=np.nan)
        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [2.1, 2.1, -1.1, -1.1]])
        wanted = np.asarray([np.nan, np.nan, np.nan])
        assert_array_almost_equal(interp(sample, method="nearest"), wanted)
        assert_array_almost_equal(interp(sample, method="linear"), wanted)
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        wanted = np.asarray([1001.1, 846.2, 555.5])
        assert_array_almost_equal(interp(sample), wanted)

    def test_nearest_compare_qhull(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values, method="nearest")
        points_qhull = itertools.product(*points)
        points_qhull = [p for p in points_qhull]
        points_qhull = np.asarray(points_qhull)
        values_qhull = values.reshape(-1)
        interp_qhull = NearestNDInterpolator(points_qhull, values_qhull)
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        assert_array_almost_equal(interp(sample), interp_qhull(sample))

    def test_linear_compare_qhull(self):
        points, values = self._get_sample_4d()
        interp = RegularGridInterpolator(points, values)
        points_qhull = itertools.product(*points)
        points_qhull = [p for p in points_qhull]
        points_qhull = np.asarray(points_qhull)
        values_qhull = values.reshape(-1)
        interp_qhull = LinearNDInterpolator(points_qhull, values_qhull)
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        assert_array_almost_equal(interp(sample), interp_qhull(sample))

    def test_duck_typed_values(self):
        x = np.linspace(0, 2, 5)
        y = np.linspace(0, 1, 7)

        values = MyValue((5, 7))

        for method in ('nearest', 'linear'):
            interp = RegularGridInterpolator((x, y), values,
                                             method=method)
            v1 = interp([0.4, 0.7])

            interp = RegularGridInterpolator((x, y), values._v,
                                             method=method)
            v2 = interp([0.4, 0.7])
            assert_allclose(v1, v2)

    def test_invalid_fill_value(self):
        np.random.seed(1234)
        x = np.linspace(0, 2, 5)
        y = np.linspace(0, 1, 7)
        values = np.random.rand(5, 7)

        # integers can be cast to floats
        RegularGridInterpolator((x, y), values, fill_value=1)

        # complex values cannot
        assert_raises(ValueError, RegularGridInterpolator,
                      (x, y), values, fill_value=1+2j)

    def test_fillvalue_type(self):
        # from #3703; test that interpolator object construction succeeds
        values = np.ones((10, 20, 30), dtype='>f4')
        points = [np.arange(n) for n in values.shape]
        xi = [(1, 1, 1)]
        interpolator = RegularGridInterpolator(points, values)
        interpolator = RegularGridInterpolator(points, values, fill_value=0.)


class MyValue(object):
    """
    Minimal indexable object
    """

    def __init__(self, shape):
        self.ndim = 2
        self.shape = shape
        self._v = np.arange(np.prod(shape)).reshape(shape)

    def __getitem__(self, idx):
        return self._v[idx]

    def __array_interface__(self):
        return None

    def __array__(self):
        raise RuntimeError("No array representation")
