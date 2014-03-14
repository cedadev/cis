from abc import ABCMeta, abstractmethod

import numpy as np

from jasmin_cis.data_io.hyperpoint import HyperPoint
import jasmin_cis.utils


class HyperPointView(object):
    """
    View of coordinates and data as HyperPoints.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __len__(self):
        pass


class UngriddedHyperPointView(HyperPointView):
    """
    List view of data points as HyperPoints.
    """
    def __init__(self, coords, data, non_masked_iteration=False):
        """
        @param coords: coordinate values at points
        @type coords: list of 1D numpy arrays or None
        @param data: data values at points (optional)
        @type data: 1D numpy array or None
        @param non_masked_iteration: if true, the default iterator omits masked points
        """
        self.data = data
        self.coords = coords
        # Data and all coordinates should have the same size.
        self.length = coords[0].size
        self.non_masked_iteration = non_masked_iteration

    def __getitem__(self, item):
        if isinstance(item, slice):
            # Cannot handle slicing.
            #TODO Should return a new UngriddedHyperPointView.
            raise NotImplementedError
        if item < 0 or item >= self.length:
            raise IndexError("list index out of range")
        val = [(c[item] if c is not None else None) for c in self.coords]
        val.append(self.data[item] if self.data is not None else None)
        return HyperPoint(*val)

    def __len__(self):
        """Returns the number of points (including masked ones)
        @return: number of points
        """
        return self.length

    def __iter__(self):
        """Iterates over all or non-masked points according to the value of non_masked_iteration
        @return: next HyperPoint
        """
        for idx in xrange(self.length):
            if self.non_masked_iteration and self.data is not None and self.data[idx] is np.ma.masked:
                continue
            yield self.__getitem__(idx)

    def iter_all_points(self):
        """Iterates over all points regardless of the value of non_masked_iteration
        @return: next HyperPoint
        """
        for idx in xrange(self.length):
            yield self.__getitem__(idx)

    def iter_non_masked_points(self):
        """Iterates over non-masked points regardless of the value of non_masked_iteration
        @return: next HyperPoint
        """
        for idx in xrange(self.length):
            if self.data is not None and self.data[idx] is np.ma.masked:
                continue
            yield self.__getitem__(idx)

    def enumerate_non_masked_points(self):
        """Iterates over non-masked points returning the index in the full
        data array and the corresponding HyperPoint.
        @return: tuple(index of point, HyperPoint)
        """
        for idx in xrange(self.length):
            if self.data is not None and self.data[idx] is np.ma.masked:
                continue
            yield (idx, self.__getitem__(idx))


class GriddedHyperPointView(HyperPointView):
    """
    List view of data points as HyperPoints.
    """
    def __init__(self, dim_coords_and_dims, data, non_masked_iteration=False, cube=None):
        """
        @param coords: coordinate values at points
        @type coords: list of tuples of (1D numpy array of coordinate values, index of corresponding dimension) or None
        @param data: data values at points
        @type data: n-D numpy array with one dimension for each coordinate
        @param non_masked_iteration: if true, the default iterator omits masked points
        """
        self.data = data
        self.num_dimensions = len(data.shape)
        self.coords = [None] * len(dim_coords_and_dims)
        self.dims_to_std_coords_map = {}
        # Determine which standard coordinate corresponds to which cube dimension.
        for sc_idx, cd in enumerate(dim_coords_and_dims):
            if cd is not None:
                self.coords[cd[1]] = cd[0]
                self.dims_to_std_coords_map[cd[1]] = sc_idx
        self.length = data.size
        self.non_masked_iteration = non_masked_iteration
        self.cube = cube

    def __getitem__(self, item):
        """Get HyperPoint specified by index.
        @param item: index of item, either a scalar int over flattened data or
                     a tuple of coordinate indices
        @type item: tuple or int
        @return: HyperPoint corresponding to data point
        """
        val = [None] * HyperPoint.number_standard_names
        if isinstance(item, tuple):
            if any(isinstance(i, slice) for i in item):
                # Cannot handle multidimensional slicing.
                raise NotImplementedError
            indices = item
        else:
            if isinstance(item, slice):
                raise NotImplementedError
            else:
                # Index is over flattened (or 1-D) data - convert to unflattened tuple of indices.
                indices = np.unravel_index(item, self.data.shape, order='C')
        for idx, coord_idx in enumerate(indices):
            coord = self.coords[idx]
            if coord is not None:
                val[self.dims_to_std_coords_map[idx]] = coord[coord_idx]
            else:
                val.append(None)
        if self.data is not None:
            val.append(self.data[indices])
        return HyperPoint(*val)

    def __len__(self):
        """Returns the number of points (including masked ones)
        @return: number of points
        """
        return self.length

    def __iter__(self):
        """Iterates over all or non-masked points according to the value of non_masked_iteration
        @return: next HyperPoint
        """
        shape = [c.size for c in self.coords if (c is not None and c.size > 1)]
        for idx in jasmin_cis.utils.index_iterator(shape):
            if self.non_masked_iteration and self.data is not None and self.data[idx] is np.ma.masked:
                continue
            yield self.__getitem__(idx)

    def iter_all_points(self):
        """Iterates over all points regardless of the value of non_masked_iteration
        @return: next HyperPoint
        """
        shape = [c.size for c in self.coords if c is not None]
        for idx in jasmin_cis.utils.index_iterator(shape):
            yield self.__getitem__(idx)

    def iter_non_masked_points(self):
        """Iterates over non-masked points regardless of the value of non_masked_iteration
        @return: next HyperPoint
        """
        shape = [c.size for c in self.coords if c is not None]
        for idx in jasmin_cis.utils.index_iterator(shape):
            if self.data is not None and self.data[idx] is np.ma.masked:
                continue
            yield self.__getitem__(idx)

    def enumerate_non_masked_points(self):
        """Iterates over non-masked points returning the index in the full
        data array and the corresponding HyperPoint.
        @return: tuple(index of point in flattened view of data, HyperPoint)
        """
        shape = tuple([c.size for c in self.coords if c is not None])
        for idx in xrange(self.length):
            if self.data is not None:
                indices = np.unravel_index(idx, shape, order='C')
                if self.data[indices] is np.ma.masked:
                    continue
            yield (idx, self.__getitem__(idx))
