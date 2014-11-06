from abc import ABCMeta
import logging
from collections import namedtuple

import numpy as np
import iris

from jasmin_cis.subsetting.subset_framework import SubsetConstraintInterface
from jasmin_cis.data_io.Coord import Coord, CoordList
import jasmin_cis.data_io.gridded_data as gridded_data
from jasmin_cis.data_io.ungridded_data import UngriddedData, UngriddedDataList


class CoordLimits(namedtuple('CoordLimits', ['coord', 'start', 'end', 'constraint_function'])):
    """Holds the start and end values for subsetting limits.
    :ivar coord: the coordinate the limit applies to
    :ivar start: subsetting limit start
    :ivar end: subsetting limit end
    :ivar constraint_function: function determining whether the constraint is satisfied
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

    def set_limit(self, coord, dim_min, dim_max, wrapped):
        """Sets boundary values for a dimension to be used in subsetting.

        :param coord: coordinate to which limit applies
        :param dim_min: lower bound on dimension or None to indicate no lower bound
        :param dim_max: upper bound on dimension or None to indicate no upper bound
        """
        if dim_min is not None or dim_max is not None:
            logging.info("Setting limit for dimension '%s' [%s, %s]", coord.name(), str(dim_min), str(dim_max))
            self._limits[coord.name()] = CoordLimits(coord, dim_min, dim_max,
                                                     self._make_constraint_function(dim_min, dim_max, wrapped))

    @staticmethod
    def _make_constraint_function(dim_min, dim_max, wrapped):
        """Constructs a function enforcing the specified bounds on the values of a dimension.

        The boundary values are included in the constrained interval.
        :param dim_min: lower bound on dimension or None to indicate no lower bound
        :param dim_max: upper bound on dimension or None to indicate no upper bound
        :param wrapped: True if the coordinate is circular and the included range is wrapped, otherwise False
        :return: lambda function with one argument returning bool
        """
        if wrapped:
            return lambda x: x >= dim_min or x <= dim_max
        else:
            return lambda x: dim_min <= x <= dim_max

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

        :return: iris.Constraint object
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

        :param data: data to be subsetted
        :type data: iris.cube.Cube
        :return: subsetted data
        @rtype: jasmin_cis.data_io.gridded_data.GriddedData
        """
        iris_constraint = self.make_iris_constraint()
        return gridded_data.make_from_cube(data.extract(iris_constraint))


class UngriddedSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting ungridded data.
    """
    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
        if isinstance(data, list):
            new_data = UngriddedDataList()
            for data in data:
                new_data.append(self.constrain(data))
            return new_data

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

        if len(new_values) > 0:
            # Collect output into object.
            new_data = np.array(new_values, dtype=data.data.dtype, copy=False)
            subset_metadata = data.metadata
            subset_metadata.shape = (len(new_values),)

            subset_coords = CoordList()
            for coord in coord_pairs:
                new_coord = Coord(np.array(coord.output, dtype=coord.input.data.dtype, copy=False),
                                  coord.input.metadata)
                new_coord.metadata.shape = (len(coord.output),)
                subset_coords.append(new_coord)
            subset = UngriddedData(new_data, subset_metadata, subset_coords)
        else:
            subset = None

        return subset
