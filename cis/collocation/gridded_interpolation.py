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
#  interpolations of different datasets using the same points, and support for hybrid coordinates.

import numpy as np


class GriddedUngriddedInterpolator(object):

    def __init__(self, data, sample, method='linear'):
        """
        Prepare an interpolation over the grid defined by a GriddedData source onto an UngriddedData sample.

        Indices are calculated but no interpolation is performed until the resulting object is called. Note that
        if the source contains a hybrid vertical coordinate these ARE interpolated to find a single vertical index.

        :param GriddedData data: The source data, only the coordinates are used from this at initialisation.
        :param UngriddedData sample: The points to sample the source data at.
        :param str method: The interpolation method to use (either 'linear' or 'nearest'). Default is 'linear'.
        """
        from iris.analysis._interpolation import extend_circular_coord
        coords = []
        grid_points = []
        self.circular_coord_dims = []
        # Remove any tuples in the list that do not correspond to a dimension coordinate in the cube 'data'.
        for coord in data.coords(dim_coords=True):
            if len(sample.coords(coord.name())) > 0:
                coords.append(coord.name())
                if getattr(coord, 'circular', False):
                    grid_points.append(extend_circular_coord(coord, coord.points))
                    # The circular coord must be a dim coord so we pop the value out of the tuple
                    self.circular_coord_dims.append(data.coord_dims(coord)[0])
                else:
                    grid_points.append(coord.points)

        sample_points = [sample.coord(c).points for c in coords]

        if len(data.coords('altitude', dim_coords=False)) > 0 and sample.coords('altitude'):
            hybrid_coord = data.coord('altitude').points
            hybrid_dims = data.coord_dims(data.coord('altitude'))
            sample_points.append(sample.coord("altitude").points)
        elif len(data.coords('air_pressure', dim_coords=False)) > 0 and sample.coords('air_pressure'):
            hybrid_coord = data.coord('air_pressure').points
            hybrid_dims = data.coord_dims(data.coord('air_pressure'))
            sample_points.append(sample.coord("air_pressure").points)
        else:
            hybrid_coord = None
            hybrid_dims = None

        if len(sample_points) != len(data.shape):
            raise ValueError("Sample points do not uniquely define gridded data source points, invalid "
                             "dimenions: {} and {} respectively".format(len(sample_points), len(data.shape)))

        self._interp = RegularGridInterpolator(grid_points, sample_points,
                                               hybrid_coord=hybrid_coord, hybrid_dims=hybrid_dims, method=method)

    def __call__(self, data, fill_value=np.nan, extrapolate=False):
        """
         Perform the prepared interpolation over the given data GriddedData object - this assumes that the coordinates
          used to initialise the interpolator are identical as those in this data object.

        If extrapolate is True then fill_value is ignored (since there will be no invalid values).

        :param GriddedData data: Data values to interpolate
        :param float fill_value: The fill value to use for sample points outside of the bounds of the data
        :param bool extrapolate: Extrapolate points outside the bounds of the data? Default False.
        :return ndarray: Interpolated values.
        """
        from iris.analysis._interpolation import extend_circular_data
        if extrapolate:
            fill_value = None

        # Account for any circular coords present
        data_array = data.data
        for dim in self.circular_coord_dims:
            data_array = extend_circular_data(data_array, dim)

        return self._interp(data_array, fill_value=fill_value)


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
    method : str
        The method of interpolation to perform. Supported are "linear" and "nearest". Default is "linear".
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

    def __init__(self, coords, points, hybrid_coord=None, hybrid_dims=None, method="linear"):
        if method == "linear":
            self._interp = self._evaluate_linear
        elif method == "nearest":
            self._interp = self._evaluate_nearest
        else:
            raise ValueError("Method '%s' is not defined" % method)

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
            points = np.vstack(points).T
            if points.shape[-1] != len(self.grid):
                raise ValueError("The requested sample points xi have dimension "
                                 "%d, but this RegularGridInterpolator has "
                                 "dimension %d" % (points.shape[1], ndim))
        else:
            ndim = len(self.grid)
            points = _ndim_coords_from_arrays(points, ndim=ndim)

        if hybrid_coord is not None:

            # Firstly interpolate over all of the dimensions except the vertical (which we assume to be the last...)
            self.indices, self.norm_distances, self.out_of_bounds = \
                self._find_indices(points[:-1], self.grid)

            # Find the dims to interpolate over for the hybrid coord
            hybrid_interp_dims = hybrid_dims[:-1]
            hybrid_indices = [self.indices[i] for i in hybrid_interp_dims]

            # Find all of the interpolated vertical columns (one for each point)
            v_coords = self._interp(hybrid_coord, hybrid_indices, self.norm_distances)

            self.indices.append(np.zeros(len(points.T), dtype=self.indices[0].dtype))
            self.norm_distances.append(np.zeros(len(points.T)))

            # Calculate and store the vertical index and weight for each point based on the interpolated vertical
            # column
            # TODO: This loop could be a bottle-neck for many points, maybe move to Cython?
            for i, p in enumerate(points.T):
                vert_index, vert_norm_distance, vert_out_of_bounds = self._find_vertical_index(p[-1], v_coords[i])
                self.indices[-1][i] = vert_index
                self.norm_distances[-1][i] = vert_norm_distance
                self.out_of_bounds[i] += vert_out_of_bounds

        else:
            self.indices, self.norm_distances, self.out_of_bounds = self._find_indices(points.T, self.grid)

    def __call__(self, values, fill_value=np.nan):
        """
        Interpolation at coordinates
        Parameters
        ----------
        values : array_like, shape (m1, ..., mn, ...)
            The data on the regular grid in n dimensions.
        fill_value : number, optional
            If provided, the value to use for points outside of the
            interpolation domain. If None, values outside
            the domain are extrapolated.
        """
        if not hasattr(values, 'ndim'):
            # allow reasonable duck-typed values
            values = np.asarray(values)

        if len(self.grid) > values.ndim:
            raise ValueError("There are %d point arrays, but values has %d "
                             "dimensions" % (len(self.grid), values.ndim))

        if hasattr(values, 'dtype') and hasattr(values, 'astype'):
            if not np.issubdtype(values.dtype, np.inexact):
                values = values.astype(float)

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

        result = self._interp(values, self.indices, self.norm_distances)

        if fill_value is not None:
            result[self.out_of_bounds] = fill_value

        return result

    @staticmethod
    def _evaluate_linear(values, indices, norm_distances):
        from itertools import product
        # slice for broadcasting over trailing dimensions in self.values
        vslice = (slice(None),) + (None,)*(values.ndim - len(indices))

        # find relevant values
        # each i and i+1 represents a edge
        edges = product(*[[i, i + 1] for i in indices])
        value = 0.
        for edge_indices in edges:
            weight = 1.
            for ei, i, yi in zip(edge_indices, indices, norm_distances):
                weight *= np.where(ei == i, 1 - yi, yi)
            value += np.asarray(values[edge_indices]) * weight[vslice]
        return value

    @staticmethod
    def _evaluate_nearest(values, indices, norm_distances):
        idx_res = []
        for i, yi in zip(indices, norm_distances):
            idx_res.append(np.where(yi <= .5, i, i + 1))
        return values[idx_res]

    @staticmethod
    def _find_indices(points, coords):
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

            norm_distances.append((x - coord[i]) / (coord[i + 1] - coord[i]))
            indices.append(i)

            out_of_bounds += x < coord[0]
            out_of_bounds += x > coord[-1]
        return indices, norm_distances, out_of_bounds

    @staticmethod
    def _find_vertical_index(point, coord):
        i = np.searchsorted(coord, point) - 1
        if i < 0:
            i = 0
        if i > coord.size - 2:
            i = coord.size - 2
        norm_distances = ((point - coord[i]) / (coord[i + 1] - coord[i]))

        out_of_bounds = point < coord[0] or point > coord[-1]
        return i, norm_distances, out_of_bounds
