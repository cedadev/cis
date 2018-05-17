# The TestRegularGridInterpolator class was adapted from the SciPy original here:
# https://github.com/scipy/scipy/blob/master/scipy/interpolate/tests/test_interpolate.py

# Copyright (c) 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright (c) 2003-2013 SciPy Developers.
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# We've changed the order in which the points and sample get passed as per our API change, but otherwise the tests are
# the same

from __future__ import division, print_function, absolute_import

import itertools
import numpy as np
from numpy.testing import (assert_array_almost_equal, assert_raises,
                           TestCase, assert_allclose)

from cis.collocation.gridded_interpolation import _RegularGridInterpolator, GriddedUngriddedInterpolator
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

        for method in ['lin', 'nn']:
            interp = _RegularGridInterpolator(points,
                                             sample.T.tolist(), method=method)
            v1 = interp(values.tolist())
            interp = _RegularGridInterpolator(points,
                                             sample.T, method=method)
            v2 = interp(values)
            assert_allclose(v1, v2)

    def test_complex(self):
        points, values = self._get_sample_4d()
        values = values - 2j*values
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8], [0.5, 0.5, .5, .5]])

        for method in ['lin', 'nn']:
            interp = _RegularGridInterpolator(points, sample.T, method=method)
            rinterp = _RegularGridInterpolator(points, sample.real.T, method=method)
            iinterp = _RegularGridInterpolator(points, sample.imag.T, method=method)

            v1 = interp(values)
            v2 = rinterp(values) + 1j*iinterp(values)
            assert_allclose(v1, v2)

    def test_linear_xi1d(self):
        points, values = self._get_sample_4d_2()
        sample = np.asarray([0.1, 0.1, 10., 9.])
        wanted = 1001.1
        interp = _RegularGridInterpolator(points, sample.T)
        assert_array_almost_equal(interp(values), wanted)

    def test_linear_xi3d(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                                                     [0.5, 0.5, .5, .5]])
        wanted = np.asarray([1001.1, 846.2, 555.5])
        interp = _RegularGridInterpolator(points, sample.T)
        assert_array_almost_equal(interp(values), wanted)

    def test_nearest(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([0.1, 0.1, .9, .9])
        wanted = 1100.
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        assert_array_almost_equal(interp(values), wanted)
        sample = np.asarray([0.1, 0.1, 0.1, 0.1])
        wanted = 0.
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        assert_array_almost_equal(interp(values), wanted)
        sample = np.asarray([0., 0., 0., 0.])
        wanted = 0.
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        assert_array_almost_equal(interp(values), wanted)
        sample = np.asarray([1., 1., 1., 1.])
        wanted = 1111.
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        assert_array_almost_equal(interp(values), wanted)
        sample = np.asarray([0.1, 0.4, 0.6, 0.9])
        wanted = 1055.
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        assert_array_almost_equal(interp(values), wanted)

    def test_linear_edges(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[0., 0., 0., 0.], [1., 1., 1., 1.]])
        wanted = np.asarray([0., 1111.])
        interp = _RegularGridInterpolator(points, sample.T)
        assert_array_almost_equal(interp(values), wanted)

    def test_valid_create(self):
        # create a 2d grid of 3 points in each dimension
        points = [(0., .5, 1.), (0., 1., .5)]
        values = np.asarray([0., .5, 1.])
        values0 = values[:, np.newaxis]
        values1 = values[np.newaxis, :]
        values = (values0 + values1 * 10)
        assert_raises(ValueError, _RegularGridInterpolator, points, values)
        points = [((0., .5, 1.), ), (0., .5, 1.)]
        assert_raises(ValueError, _RegularGridInterpolator, points, values)
        points = [(0., .5, .75, 1.), (0., .5, 1.)]
        assert_raises(ValueError, _RegularGridInterpolator, points, values)

    def test_valid_call(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[0., 0., 0., 0.], [1., 1., 1., 1.]])
        interp = _RegularGridInterpolator(points, sample.T)
        assert_raises(ValueError, interp, values, "undefmethod")
        # This is actually an error on creation now
        sample = np.asarray([[0., 0., 0.], [1., 1., 1.]])
        assert_raises(ValueError, _RegularGridInterpolator, points, sample)

    def test_out_of_bounds_extrap(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [21, 2.1, -1.1, -11], [2.1, 2.1, -1.1, -1.1]])
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        wanted = np.asarray([0., 1111., 11., 11.])
        assert_array_almost_equal(interp(values, fill_value=None), wanted)
        interp = _RegularGridInterpolator(points, sample.T, method="lin")
        wanted = np.asarray([-111.1, 1222.1, -11068., -1186.9])
        assert_array_almost_equal(interp(values, fill_value=None), wanted)

    def test_out_of_bounds_extrap2(self):
        points, values = self._get_sample_4d_2()
        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [21, 2.1, -1.1, -11], [2.1, 2.1, -1.1, -1.1]])

        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        wanted = np.asarray([0., 11., 11., 11.])
        assert_array_almost_equal(interp(values, fill_value=None), wanted)
        interp = _RegularGridInterpolator(points, sample.T, method="lin")
        wanted = np.asarray([-12.1, 133.1, -1069., -97.9])
        assert_array_almost_equal(interp(values, fill_value=None), wanted)

    def test_out_of_bounds_fill(self):
        points, values = self._get_sample_4d()

        sample = np.asarray([[-.1, -.1, -.1, -.1], [1.1, 1.1, 1.1, 1.1],
                             [2.1, 2.1, -1.1, -1.1]])
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        # Assert that all of the elements are masked
        assert all(interp(values, fill_value=np.nan).mask)
        interp = _RegularGridInterpolator(points, sample.T, method="lin")
        assert all(interp(values, fill_value=np.nan).mask)

        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        wanted = np.asarray([1001.1, 846.2, 555.5])
        interp = _RegularGridInterpolator(points, sample.T)
        assert_array_almost_equal(interp(values, fill_value=np.nan), wanted)

    def test_nearest_compare_qhull(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        interp = _RegularGridInterpolator(points, sample.T, method="nn")
        points_qhull = itertools.product(*points)
        points_qhull = [p for p in points_qhull]
        points_qhull = np.asarray(points_qhull)
        values_qhull = values.reshape(-1)
        interp_qhull = NearestNDInterpolator(points_qhull, values_qhull)
        assert_array_almost_equal(interp(values), interp_qhull(sample))

    def test_linear_compare_qhull(self):
        points, values = self._get_sample_4d()
        sample = np.asarray([[0.1, 0.1, 1., .9], [0.2, 0.1, .45, .8],
                             [0.5, 0.5, .5, .5]])
        interp = _RegularGridInterpolator(points, sample.T)
        points_qhull = itertools.product(*points)
        points_qhull = [p for p in points_qhull]
        points_qhull = np.asarray(points_qhull)
        values_qhull = values.reshape(-1)
        interp_qhull = LinearNDInterpolator(points_qhull, values_qhull)
        assert_array_almost_equal(interp(values), interp_qhull(sample))

    def test_2d_cube(self):
        from cis.test.util.mock import make_square_5x3_2d_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint

        cube = make_square_5x3_2d_cube()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        values = interpolator(cube)
        wanted = np.asarray([8.8, 11.2, 4.8])
        assert_array_almost_equal(values, wanted)

    def test_hybrid_Coord_nn(self):
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint
        import datetime as dt
        cube = make_mock_cube(time_dim_length=3, hybrid_pr_len=10)

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, alt=5000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=0.0, lon=0.0, pres=113625040.5, alt=4000, t=dt.datetime(1984, 8, 28, 12, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, alt=3000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=-4.0, lon=-4.0, pres=166600039.0, alt=3500, t=dt.datetime(1984, 8, 27))])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'nn')
        values = interpolator(cube)
        wanted = np.ma.masked_invalid(np.ma.array([221.0, 223.0, 318.0, np.nan]))
        assert_array_almost_equal(values, wanted)

    def test_hybrid_Coord_without_hybrid_coord(self):
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint
        import datetime as dt
        cube = make_mock_cube(time_dim_length=3)

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 28, 12, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=-4.0, lon=-4.0, t=dt.datetime(1984, 8, 27))])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        values = interpolator(cube)
        wanted = np.asarray([23.0, 23.5, 33.5, 12.4])
        assert_array_almost_equal(values, wanted)

    def test_hybrid_Coord(self):
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint
        import datetime as dt
        cube = make_mock_cube(time_dim_length=3, hybrid_pr_len=10)

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, alt=5000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=0.0, lon=0.0, pres=113625040.5, alt=4000, t=dt.datetime(1984, 8, 28, 12, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, alt=3000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=-4.0, lon=-4.0, pres=166600039.0, alt=3500, t=dt.datetime(1984, 8, 27))])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        values = interpolator(cube)
        wanted = np.ma.masked_invalid(np.ma.array([221.5, 226.5, 330.5, np.nan]))
        assert_array_almost_equal(values, wanted)

    def test_hybrid_pres_Coord_order_doesnt_matter(self):
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint
        import datetime as dt
        cube = make_mock_cube(time_dim_length=3, hybrid_pr_len=10)

        cube.transpose()

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, alt=5000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=0.0, lon=0.0, pres=113625040.5, alt=4000, t=dt.datetime(1984, 8, 28, 12, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, alt=3000, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=-4.0, lon=-4.0, pres=166600039.0, alt=3500, t=dt.datetime(1984, 8, 27))])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        values = interpolator(cube)
        wanted = np.ma.masked_invalid(np.ma.array([221.5, 226.5, 330.5, np.nan]))
        assert_array_almost_equal(values, wanted)

    def test_hybrid_alt_Coord_order_doesnt_matter(self):
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint
        import datetime as dt
        cube = make_mock_cube(time_dim_length=3, hybrid_ht_len=10)

        cube.transpose()

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=5000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'nn')
        values = interpolator(cube, fill_value=None)
        wanted = np.asarray([221.0, 345.0, 100.0])
        assert_array_almost_equal(values, wanted)

    def test_invalid_fill_value(self):
        np.random.seed(1234)
        x = np.linspace(0, 2, 5)
        y = np.linspace(0, 1, 7)
        values = np.random.rand(5, 7)

        # integers can be cast to floats
        interp = _RegularGridInterpolator((x, y), [0.4, 0.7])
        interp(values, fill_value=1)

        # complex values cannot
        assert_raises(ValueError, interp, values, fill_value=1+2j)

    def test_fillvalue_type(self):
        # from #3703; test that interpolator object construction succeeds
        values = np.ones((10, 20, 30), dtype='>f4')
        points = [np.arange(n) for n in values.shape]
        xi = np.asarray([1, 1, 1])
        interpolator = _RegularGridInterpolator(points, xi.T)
        interpolator(values, fill_value=0.)

    def test_missing_values(self):
        from cis.test.util.mock import make_square_5x3_2d_cube_with_missing_data

        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint

        cube = make_square_5x3_2d_cube_with_missing_data()

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0),
             HyperPoint(lat=0.0, lon=4.0),
             HyperPoint(lat=-4.0, lon=1.0)])

        wanted = np.ma.array([8.0, np.nan, np.nan], mask=[False, True, True])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'nn')
        assert_array_almost_equal(interpolator(cube), wanted)

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        assert_array_almost_equal(interpolator(cube), wanted)

    def test_missing_values_with_extrapolation(self):
        from cis.test.util.mock import make_square_5x3_2d_cube_with_missing_data

        from cis.data_io.ungridded_data import UngriddedData
        from cis.data_io.hyperpoint import HyperPoint

        cube = make_square_5x3_2d_cube_with_missing_data()

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=-5.0, lon=10.0),
             HyperPoint(lat=0.0, lon=10.0),
             HyperPoint(lat=-4.0, lon=1.0)])

        wanted = np.ma.array([6.0, np.nan, np.nan], mask=[False, True, True])

        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'nn')
        assert_array_almost_equal(interpolator(cube, extrapolate=True), wanted)

        wanted = np.ma.array([7.0, np.nan, np.nan], mask=[False, True, True])
        interpolator = GriddedUngriddedInterpolator(cube, sample_points, 'lin')
        assert_array_almost_equal(interpolator(cube, extrapolate=True), wanted)


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
