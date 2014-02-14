from abc import ABCMeta
import logging
from collections import namedtuple

import numpy as np
import iris

from jasmin_cis.subsetting.subset_framework import SubsetConstraintInterface
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData


class CoordLimits(namedtuple('CoordLimits', ['coord', 'start', 'end', 'constraint_function'])):
    """Holds the start and end values for subsetting limits.
    @ivar coord: the coordinate the limit applies to
    @ivar start: subsetting limit start
    @ivar end: subsetting limit end
    @ivar constraint_function: function determining whether the constraint is satisfied
    """
    pass


class SubsetConstraint(SubsetConstraintInterface):
    """Abstract Constraint for subsetting.

    Holds the limits for subsetting in each dimension.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._limits = {}
        logging.debug("Created SubsetConstraint of type %s", self.__class__.__name__)

    def set_limit(self, coord, dim_min, dim_max):
        """Sets boundary values for a dimension to be used in subsetting.

        @param coord: coordinate to which limit applies
        @param dim_min: lower bound on dimension or None to indicate no lower bound
        @param dim_max: upper bound on dimension or None to indicate no upper bound
        """
        if dim_min is not None or dim_max is not None:
            logging.info("Setting limit for dimension '%s' [%s, %s]", coord.name(), str(dim_min), str(dim_max))
            self._limits[coord.name()] = CoordLimits(coord, dim_min, dim_max,
                                                     self._make_constraint_function(dim_min, dim_max))

    @staticmethod
    def _make_constraint_function(dim_min, dim_max):
        """Constructs a function enforcing the specified bounds on the values of a dimension.

        The boundary values are included in the constrained interval.
        @param dim_min: lower bound on dimension or None to indicate no lower bound
        @param dim_max: upper bound on dimension or None to indicate no upper bound
        @return: lambda function with one argument returning bool
        """
        if dim_min is not None and dim_max is not None:
            return lambda x: dim_min <= x <= dim_max
        elif dim_min is not None and dim_max is None:
            return lambda x: dim_min <= x
        elif dim_min is None and dim_max is not None:
            return lambda x: x <= dim_max
        else:
            return None

    def __str__(self):
        limit_strs = []
        for name, limit in self._limits.iteritems():
            limit_strs.append("{}: [{}, {}]".format(name, str(limit.start), str(limit.end)))
        return ', '.join(limit_strs)


class GriddedSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting gridded data.
    """
    def make_iris_constraint(self):
        """Constructs an Iris constraint corresponding to the limits set for each dimension.

        @return: iris.Constraint object
        """
        constraint = None
        for coord, limits in self._limits.iteritems():
            constraint_function = limits.constraint_function
            if constraint is None:
                constraint = iris.Constraint(**{coord: constraint_function})
            else:
                constraint = constraint & iris.Constraint(**{coord: constraint_function})
        return constraint

    def constrain(self, data):
        """Subsets the supplied data.

        @param data: data to be subsetted
        @type data: iris.cube.Cube
        @return: subsetted data
        @rtype: iris.cube.Cube
        """
        iris_constraint = self.make_iris_constraint()
        return data.extract(iris_constraint)


class UngriddedSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting ungridded data.
    """
    def constrain(self, data):
        """Subsets the supplied data.

        @param data: data to be subsetted
        @return: subsetted data
        """
        CoordPair = namedtuple('CoordPair', ['input', 'output'])

        new_values = []
        coord_pairs = []
        for coord in data.coords():
            coord_pairs.append(CoordPair(coord, []))

        # Filter points to include in subset.
        is_masked = isinstance(data.data, np.ma.masked_array)
        missing_value = data.metadata.missing_value
        for idx, value in enumerate(data.data.flat):
            if is_masked and value is np.ma.masked:
                value = missing_value
                # continue

            include = True
            for limit in self._limits.itervalues():
                if not limit.constraint_function(limit.coord.data_flattened[idx]):
                    include = False
                    break
            if include:
                # Append coordinates and value.
                new_values.append(value)
                for coord in coord_pairs:
                    coord.output.append(coord.input.data_flattened[idx])

        # Collect output into object.
        new_data = np.array(new_values, dtype=data.data.dtype, copy=False)
        subset_metadata = data.metadata
        subset_metadata.shape = (len(new_values),)

        subset_coords = CoordList()
        for coord in coord_pairs:
            new_coord = Coord(np.array(coord.output, copy=False), coord.input.metadata)
            new_coord.metadata.shape = (len(coord.output),)
            subset_coords.append(new_coord)
        subset = UngriddedData(new_data, subset_metadata, subset_coords)

        return subset


class UngriddedOnGridSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting data held in
    an UngriddedData object but which has coordinates on a grid.
    """
    def constrain(self, data):
        """Subsets the supplied data.

        @param data: data to be subsetted
        @return: subsetted data
        """
        shape = data.data.shape
        ndim = len(shape)
        #TODO Coordinates should have the same shape.

        # Initialise arrays for new values and slices that are included in the subset.
        min_indices = list(shape)
        max_indices = [0] * ndim

        # Filter points to include in subset.
        for idx in _index_iterator(shape):
            include = True
            for limit in self._limits.itervalues():
                if not limit.constraint_function(limit.coord.data[idx]):
                    include = False
                    break
            if include:
                # Append coordinates and value.
                for j in range(ndim):
                    if idx[j] > max_indices[j]:
                        max_indices[j] = idx[j]
                    if idx[j] < min_indices[j]:
                        min_indices[j] = idx[j]

        # Construct slices and shape representing the region allowed by the constraints.
        slice_list = []
        shape_list = []
        num_values = 1
        for j in range(ndim):
            slice_list.append(slice(min_indices[j], max_indices[j]))
            shape_list.append(max_indices[j] - min_indices[j])
            num_values *= (max_indices[j] - min_indices[j])
        slice_tuple = tuple(slice_list)
        shape_tuple = tuple(shape_list)

        if num_values > 0:
            # Collect output into object.
            new_data = np.array(data.data[slice_tuple], copy=False)
            subset_metadata = data.metadata
            subset_metadata.shape = shape_tuple

            subset_coords = CoordList()
            for coord in data.coords():
                coord_metadata = coord.metadata
                coord_metadata.shape = shape_tuple
                new_coord = Coord(np.array(coord.data[slice_tuple], copy=False), coord_metadata)
                subset_coords.append(new_coord)
            subset = UngriddedData(new_data, subset_metadata, subset_coords)
        else:
            subset = None
        return subset


def _index_iterator(shape):
    """Iterates over the indexes of a multi-dimensional array of a specified shape.

    The last index changes most rapidly.
    @param shape: sequence of array dimensions
    @return: yields tuples of array indexes
    """
    dim = len(shape)
    idx = [0] * dim
    num_iterations = 1
    for j in range(0, dim):
        num_iterations *= shape[j]

    for iterations in range(num_iterations):
        yield tuple(idx)
        for j in range(dim - 1, -1, -1):
            idx[j] += 1
            if idx[j] < shape[j]:
                break
            idx[j] = 0
