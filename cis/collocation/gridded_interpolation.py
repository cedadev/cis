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
# The two helper functions extend_circular_coord and _data are also taken from SciPy as the interpolate module is
#  deprecated since Iris 1.10.
import numpy as np


def extend_circular_coord(coord, points):
    """
    Return coordinates points with a shape extended by one
    This is common when dealing with circular coordinates.

    """
    modulus = np.array(coord.units.modulus or 0,
                       dtype=coord.dtype)
    points = np.append(points, points[0] + modulus)
    return points


def extend_circular_data(data, coord_dim):
    coord_slice_in_cube = [slice(None)] * data.ndim
    coord_slice_in_cube[coord_dim] = slice(0, 1)

    data = np.append(data,
                     data[tuple(coord_slice_in_cube)],
                     axis=coord_dim)
    return data


class GriddedUngriddedInterpolator(object):

    def __init__(self, _data, sample, method='lin', missing_data_for_missing_sample=False):
        """
        Prepare an interpolation over the grid defined by a GriddedData source onto an UngriddedData sample.

        Indices are calculated but no interpolation is performed until the resulting object is called. Note that
        if the source contains a hybrid vertical coordinate these ARE interpolated to find a single vertical index.

        :param GriddedData _data: The source data, only the coordinates are used from this at initialisation.
        :param UngriddedData sample: The points to sample the source data at.
        :param str method: The interpolation method to use (either 'linear' or 'nearest'). Default is 'linear'.
        """
        from cis.utils import move_item_to_end
        coords = []
        grid_points = []
        self._circular_coord_dims = []
        self._decreasing_coord_dims = []

        # If we have hybrid coordinates then ensure that the vertical dimension of the cube is last, as we will be
        #  performing partial interpolations to pull out vertical columns - which only works if the vertical dim is last
        # We do this first so that the coordinates are pulled out in the correct, new, order.
        if len(_data.aux_factories) > 0:
            vertical_dim = _data.coord_dims(_data.aux_factories[0].sigma)[0]
            self._data_transpose = move_item_to_end(range(_data.ndim), vertical_dim)
        else:
            self._data_transpose = list(range(_data.ndim))

        # Unfortunately transpose works in place, so make a copy of the data first
        data = _data.copy()
        data.transpose(self._data_transpose)

        # Remove any tuples in the list that do not correspond to a dimension coordinate in the cube 'data'.
        for coord in data.coords(dim_coords=True):
            if len(sample.coords(standard_name=coord.name())) > 0:
                coords.append(coord.name())
                # The circular coord must be a dim coord so we pop the value out of the tuple
                coord_dim = data.coord_dims(coord)[0]
                coord_points = coord.points

                decreasing = (coord_points.size > 1 and
                              coord_points[1] < coord_points[0])
                if decreasing:
                    self._decreasing_coord_dims.append(decreasing)
                    coord_points = coord_points[::-1]

                if getattr(coord, 'circular', False):
                    self._circular_coord_dims.append(coord_dim)
                    coord_points = extend_circular_coord(coord, coord_points)

                grid_points.append(coord_points)

        sample_points = [sample.coord(c).data_flattened for c in coords]

        if len(data.coords('altitude', dim_coords=False)) > 0 and sample.coords(standard_name='altitude'):
            hybrid_dims = data.coord_dims(data.coord('altitude'))
            hybrid_coord = data.coord('altitude').points
            for coord_dim in self._circular_coord_dims:
                # Lookup the dimension on the hybrid data array
                hybrid_coord_dim = hybrid_dims.index(coord_dim)
                hybrid_coord = extend_circular_data(hybrid_coord, hybrid_coord_dim)
            sample_points.append(sample.coord(standard_name="altitude").data_flattened)
        elif len(data.coords('air_pressure', dim_coords=False)) > 0 and sample.coords(standard_name='air_pressure'):
            hybrid_coord = data.coord('air_pressure').points
            for coord_dim in self._circular_coord_dims:
                hybrid_coord = extend_circular_data(hybrid_coord, coord_dim)
            hybrid_dims = data.coord_dims(data.coord('air_pressure'))
            sample_points.append(sample.coord(standard_name="air_pressure").data_flattened)
        else:
            hybrid_coord = None
            hybrid_dims = None

        if len(sample_points) != len(data.shape):
            raise ValueError("Sample points do not uniquely define gridded data source points, invalid "
                             "dimenions: {} and {} respectively".format(len(sample_points), len(data.shape)))

        # Check if we want to sample missing points
        if missing_data_for_missing_sample and hasattr(sample.data, 'mask'):
            self.missing_mask = sample.data.mask.flatten()
            sample_points = [p[~self.missing_mask] for p in sample_points]
        else:
            self.missing_mask = None

        self._interp = _RegularGridInterpolator(grid_points, sample_points,
                                                hybrid_coord=hybrid_coord, hybrid_dims=hybrid_dims, method=method)

    def _get_dims_order(self, data, coords):
        """
        Return the dims with the vertical coord last. There must be a nicer way of doing this...
        """
        # Find the only dimension coordinate we haven't yet accounted for - this must be the vertical
        vertical_coord = list(set([c.name() for c in data.coords(dim_coords=True)]).difference(set(coords)))[0]
        vertical_dim = data.coord_dims(vertical_coord)[0]
        # The dim order is just the range of the dims with the vertical dim moved to the end.
        self._data_transpose.pop(vertical_dim)
        self._data_transpose.append(vertical_dim)

    def _account_for_inverted(self, data):
        dim_slices = [slice(None)] * data.ndim
        for dim in self._decreasing_coord_dims:
                dim_slices[dim] = slice(-1, None, -1)
        data = data[tuple(dim_slices)]
        return data

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
        if extrapolate:
            fill_value = None

        # Apply a transpose if we need to so that the indices line-up correctly
        data_array = data.data.transpose(self._data_transpose)
        # Account for any circular coords present
        for dim in self._circular_coord_dims:
            data_array = extend_circular_data(data_array, dim)

        data_array = self._account_for_inverted(data_array)

        result = self._interp(data_array, fill_value=fill_value)

        if self.missing_mask is not None:
            # Pack the interpolated values back into the original shape
            expanded_result = np.ma.masked_array(np.zeros(self.missing_mask.shape), mask=self.missing_mask.copy(),
                                                 fill_value=fill_value)
            expanded_result[~self.missing_mask] = result
            result = expanded_result

        return result


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


class _RegularGridInterpolator(object):
    """
    Interpolation on a regular grid in arbitrary dimensions
    The data must be defined on a regular grid; the grid spacing however may be
    uneven.  Linear and nearest-neighbour interpolation are supported. After
    setting up the interpolator object, the interpolation can be performed for
    multiple data arrays with cached indices - this assumes they have the same
    coordinates.
    """
    # this class is based on code originally programmed by Johannes Buchner,
    # see https://github.com/JohannesBuchner/regulargrid

    def __init__(self, coords, points, hybrid_coord=None, hybrid_dims=None, method="lin"):
        """
        Initialise the itnerpolator - this will calculate and cache the indices of the interpolation. It will
        also interpolate the hybrid coordinate if needed to determine a unique vertical index.

        :param iterable coords: The coords defining the regular grid in n dimensions. Should be a tuple of ndarrays
        :param ndarray points: The points to sample the gridded data at.
        :param ndarray hybrid_coord: An (optional) array describing a single vertical hybrid coordinate
        :param iterable hybrid_dims: The grid dimensions over which the hybrid coordinate is defined
        :param str method: The method of interpolation to perform. Supported are "linear" and "nearest". Default is
        "linear".
        """
        if method == "lin":
            self._interp = self._evaluate_linear
        elif method == "nn":
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
                raise ValueError("The requested sample points have dimension "
                                 "%d, but the interpolation grid has "
                                 "dimension %d" % (points.shape[1], ndim))
        else:
            ndim = len(self.grid)
            points = _ndim_coords_from_arrays(points, ndim=ndim)

        if hybrid_coord is not None:

            # Firstly interpolate over all of the dimensions except the vertical (which will always be the last...)
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
        Interpolation of values at cached coordinates

        :param ndarray values: The data on the regular grid in n dimensions
        :param float fill_value: If provided, the value to use for points outside of the interpolation domain. If None,
        values outside the domain are extrapolated.
        :return ndarray: The interpolated values
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
            result = np.ma.array(result, mask=self.out_of_bounds, fill_value=fill_value)

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
            value += np.ma.asarray(values[edge_indices]) * weight[vslice]
        return value

    @staticmethod
    def _evaluate_nearest(values, indices, norm_distances):
        idx_res = []
        for i, yi in zip(indices, norm_distances):
            idx_res.append(np.where(yi <= .5, i, i + 1))
        return values[tuple(idx_res)]

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
