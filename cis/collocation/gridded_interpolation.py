# The RegularGridInterpolator class was adapted from the SciPy original here:
# https://github.com/scipy/scipy/blob/master/scipy/interpolate/interpolate.py

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


# There is no algorithmic change, just a restructuring to allow caching of the weights for calculating many
#  interpolations of different datasets using the same points.

import itertools
import numpy as np


def interpolate(data, sample, method, fill_value=np.nan):
    """
    Interpolate a given GriddedData source onto an UngriddedData sample

     This method should take care of any
    :param GriddedData data:
    :param UngriddedData source:
    :param str method:
    :return ndarray: Interpolated values
    """
    # TODO Finish me! I should either take many gridded objects or allow caching of the interpolator somehow
    coords = []
    # Remove any tuples in the list that do not correspond to a dimension coordinate in the cube 'data'.
    for coord in sample.coords():
        if len(data.coords(coord.name(), dim_coords=True)) > 0:
            coords.append(coord.name())

    sample_points = [sample.coord(c).points for c in coords]

    if len(data.coords('altitude', dim_coords=False)) > 0 and sample.coords('altitude') is not None:
        hybrid_coord = data.coord('altitude').points
        sample_points.append(sample.coord("altitude").points)
    elif len(data.coords('air_pressure', dim_coords=False)) > 0 and sample.coords('air_pressure') is not None:
        hybrid_coord = data.coord('air_pressure').points
        sample_points.append(sample.coord("air_pressure").points)
    else:
        hybrid_coord=None

    interp = RegularGridInterpolator([data.coord(c).points for c in coords], sample_points,
                                     hybrid_coord=hybrid_coord, method=method)

    # indices = [[1 1 2 1] [ 0 0 1 0]]
    # These seem right, so it must be something to do with the vertical interp. The pressure does increase as expected
    #  so it can't be that...
    return interp(data.data, fill_value=fill_value)


def _ndim_coords_from_arrays(points, ndim=None):
    """
    Convert a tuple of coordinate arrays to a (..., ndim)-shaped array.

    """
    if isinstance(points, tuple) and len(points) == 1:
        # handle argument tuple
        points = points[0]
    if isinstance(points, tuple):
        p = np.broadcast_arrays(*points)
        for j in range(1, len(p)):
            if p[j].shape != p[0].shape:
                raise ValueError(
                    "coordinate arrays do not have the same shape")
        points = np.empty(p[0].shape + (len(points),), dtype=float)
        for j, item in enumerate(p):
            points[..., j] = item
    else:
        points = np.asanyarray(points)
        # XXX Feed back to scipy.
        if points.ndim <= 1:
            if ndim is None:
                points = points.reshape(-1, 1)
            else:
                points = points.reshape(-1, ndim)
    return points


class RegularGridInterpolator(object):
    """
    Interpolation on a regular grid in arbitrary dimensions
    The data must be defined on a regular grid; the grid spacing however may be
    uneven.  Linear and nearest-neighbour interpolation are supported. After
    setting up the interpolator object, the interpolation method (*linear* or
    *nearest*) may be chosen at each evaluation.
    Parameters
    ----------
    coords : tuple of ndarray of float, with shapes (m1, ), ..., (mn, )
        The coords defining the regular grid in n dimensions.
    points : ndarray of shape (..., ndim)
        The points to sample the gridded data at
    method : str, optional
        The method of interpolation to perform. Supported are "linear" and
        "nearest". This parameter will become the default for the object's
        ``__call__`` method. Default is "linear".
    fill_value : number, optional
        If provided, the value to use for points outside of the
        interpolation domain. If None, values outside
        the domain are extrapolated.
    Methods
    -------
    __call__
    Notes
    -----
    Contrary to LinearNDInterpolator and NearestNDInterpolator, this class
    avoids expensive triangulation of the input data by taking advantage of the
    regular grid structure.
    .. versionadded:: 0.14
    Examples
    --------
    Evaluate a simple example function on the points of a 3D grid:
    >>> from scipy.interpolate import RegularGridInterpolator
    >>> def f(x,y,z):
    ...     return 2 * x**3 + 3 * y**2 - z
    >>> x = np.linspace(1, 4, 11)
    >>> y = np.linspace(4, 7, 22)
    >>> z = np.linspace(7, 9, 33)
    >>> data = f(*np.meshgrid(x, y, z, indexing='ij', sparse=True))
    ``data`` is now a 3D array with ``data[i,j,k] = f(x[i], y[j], z[k])``.
    Next, define an interpolating function from this data:
    >>> my_interpolating_function = RegularGridInterpolator((x, y, z), data)
    Evaluate the interpolating function at the two points
    ``(x,y,z) = (2.1, 6.2, 8.3)`` and ``(3.3, 5.2, 7.1)``:
    >>> pts = np.array([[2.1, 6.2, 8.3], [3.3, 5.2, 7.1]])
    >>> my_interpolating_function(pts)
    array([ 125.80469388,  146.30069388])
    which is indeed a close approximation to
    ``[f(2.1, 6.2, 8.3), f(3.3, 5.2, 7.1)]``.
    See also
    --------
    NearestNDInterpolator : Nearest neighbour interpolation on unstructured
                            data in N dimensions
    LinearNDInterpolator : Piecewise linear interpolant on unstructured data
                           in N dimensions
    References
    ----------
    .. [1] Python package *regulargrid* by Johannes Buchner, see
           https://pypi.python.org/pypi/regulargrid/
    .. [2] Trilinear interpolation. (2013, January 17). In Wikipedia, The Free
           Encyclopedia. Retrieved 27 Feb 2013 01:28.
           http://en.wikipedia.org/w/index.php?title=Trilinear_interpolation&oldid=533448871
    .. [3] Weiser, Alan, and Sergio E. Zarantonello. "A note on piecewise linear
           and multilinear table interpolation in many dimensions." MATH.
           COMPUT. 50.181 (1988): 189-196.
           http://www.ams.org/journals/mcom/1988-50-181/S0025-5718-1988-0917826-0/S0025-5718-1988-0917826-0.pdf
    """
    # this class is based on code originally programmed by Johannes Buchner,
    # see https://github.com/JohannesBuchner/regulargrid

    def __init__(self, coords, points, hybrid_coord=None, method="linear"):
        if method not in ["linear", "nearest"]:
            raise ValueError("Method '%s' is not defined" % method)
        self.method = method

        for i, c in enumerate(coords):
            if not np.all(np.diff(c) > 0.):
                raise ValueError("The points in dimension %d must be strictly "
                                 "ascending" % i)
            if not np.asarray(c).ndim == 1:
                raise ValueError("The points in dimension %d must be "
                                 "1-dimensional" % i)
        self.grid = tuple([np.asarray(c) for c in coords])

        if hybrid_coord is None:
            ndim = len(self.grid)

            # points = _ndim_coords_from_arrays(points, ndim=ndim)
            points = np.vstack(points).T
            if points.shape[-1] != len(self.grid):
                raise ValueError("The requested sample points xi have dimension "
                                 "%d, but this RegularGridInterpolator has "
                                 "dimension %d" % (points.shape[1], ndim))
        else:
            # TODO: Think about how to calculate ndim coords when there is a hybrid coord
            ndim = len(self.grid)
            points = _ndim_coords_from_arrays(points, ndim=ndim)


        if hybrid_coord is not None:
            # Find the indices and weights of altitude columns
            # TODO: I think for hybrid altitude coords (as opposed to pressure) I'll have to work out which hybrid
            #  dimensions to interpolate over (as it doesn't vary with time).
            # Create an array to store the indices in. The _find_indices method returns a list of arrays but we can
            #  still unpack these into an array - we need to transpose it later on for the vertical part...
            self.indices = np.zeros((ndim+1, len(points)), dtype=np.int64)
            self.indices[:-1, :], self.norm_distances, self.out_of_bounds = \
                self._find_indices(points[:-1], self.grid)

            self.norm_distances.append(np.zeros(len(points)))

            # Calculate and store the verticlal index and weight for each point
            # TODO: This loop could be a bottle-neck for many points, maybe move to Cython?
            for i, p in enumerate(points.T):
                vert_index, vert_norm_distance, vert_out_of_bounds = \
                    self._find_vertical_index(p[-1], hybrid_coord[tuple(self.indices.T[i][:-1])])
                self.indices[-1][i] = vert_index
                self.norm_distances[-1][i] = vert_norm_distance
                self.out_of_bounds[i] += vert_out_of_bounds

        else:
            self.indices, self.norm_distances, self.out_of_bounds = self._find_indices(points.T, self.grid)

    def __call__(self, values, method=None, fill_value=np.nan):
        """
        Interpolation at coordinates
        Parameters
        ----------
        values : array_like, shape (m1, ..., mn, ...)
            The data on the regular grid in n dimensions.
        method : str
            The method of interpolation to perform. Supported are "linear" and
            "nearest".
        """
        method = self.method if method is None else method
        if method not in ["linear", "nearest"]:
            raise ValueError("Method '%s' is not defined" % method)

        if not hasattr(values, 'ndim'):
            # allow reasonable duck-typed values
            values = np.asarray(values)

        if len(self.grid) > values.ndim:
            raise ValueError("There are %d point arrays, but values has %d "
                             "dimensions" % (len(self.grid), values.ndim))

        if hasattr(values, 'dtype') and hasattr(values, 'astype'):
            if not np.issubdtype(values.dtype, np.inexact):
                values = values.astype(float)

        self.fill_value = fill_value
        if fill_value is not None:
            fill_value_dtype = np.asarray(fill_value).dtype
            if (hasattr(values, 'dtype') and not
                    np.can_cast(fill_value_dtype, values.dtype,
                                        casting='same_kind')):
                raise ValueError("fill_value must be either 'None' or "
                                 "of a type compatible with values")

        for i, p in enumerate(self.grid):
            if not values.shape[i] == len(p):
                raise ValueError("There are %d points and %d values in "
                                 "dimension %d" % (len(p), values.shape[i], i))

        if method == "linear":
            result = self._evaluate_linear(values)
        elif method == "nearest":
            result = self._evaluate_nearest(values)

        if self.fill_value is not None:
            result[self.out_of_bounds] = self.fill_value

        return result

    def _evaluate_linear(self, values):
        # slice for broadcasting over trailing dimensions in self.values
        vslice = (slice(None),) + (None,)*(values.ndim - len(self.indices))

        # find relevant values
        # each i and i+1 represents a edge
        edges = itertools.product(*[[i, i + 1] for i in self.indices])
        value = 0.
        for edge_indices in edges:
            weight = 1.
            for ei, i, yi in zip(edge_indices, self.indices, self.norm_distances):
                weight *= np.where(ei == i, 1 - yi, yi)
            value += np.asarray(values[edge_indices]) * weight[vslice]
        return value

    def _evaluate_nearest(self, values):
        idx_res = []
        for i, yi in zip(self.indices, self.norm_distances):
            idx_res.append(np.where(yi <= .5, i, i + 1))
        return values[idx_res]

    def _find_indices(self, points, coords):
        # find relevant edges between which xi are situated
        indices = []
        # compute distance to lower edge in unity units
        norm_distances = []
        # check for out of bounds xi
        out_of_bounds = np.zeros((points.shape[1]), dtype=bool) if isinstance(points, np.ndarray) else 0
        # iterate through dimensions
        for x, coord in zip(points, coords):
            i = np.searchsorted(coord, x) - 1
            i[i < 0] = 0
            i[i > coord.size - 2] = coord.size - 2
            indices.append(i)
            norm_distances.append((x - coord[i]) /
                                  (coord[i + 1] - coord[i]))

            out_of_bounds += x < coord[0]
            out_of_bounds += x > coord[-1]
        return indices, norm_distances, out_of_bounds

    def _find_vertical_index(self, point, coord):
        i = np.searchsorted(coord, point) - 1
        if i < 0:
            i = 0
        if i > coord.size - 2:
            i = coord.size - 2
        norm_distances = ((point - coord[i]) / (coord[i + 1] - coord[i]))

        out_of_bounds = point < coord[0] or point > coord[-1]
        return i, norm_distances, out_of_bounds
