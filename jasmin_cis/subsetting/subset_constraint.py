from abc import ABCMeta
import logging
from collections import namedtuple

import numpy as np
import iris

from jasmin_cis.subsetting.subset_framework import SubsetConstraintInterface
import jasmin_cis.data_io.gridded_data as gridded_data


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
        import numpy as np

        # Create the combined mask across all limits
        shape = data.coords()[0].data_flattened.shape  # This assumes they are all the same shape
        combined_mask = np.zeros(shape, dtype=bool)
        for limit in self._limits.itervalues():
            mask = np.zeros(shape, dtype=bool)
            for idx, val in enumerate(limit.coord.data_flattened):
                if not limit.constraint_function(val):
                    mask[idx] = True
            combined_mask = combined_mask | mask

        # Generate the new coordinates here (before we loop)
        new_coords = data.coords()
        for coord in new_coords:
            coord.data = np.ma.masked_array(coord.data, mask=combined_mask)
            coord.data = coord.data.compressed()
            coord.metadata.shape = coord.data.shape
            coord._data_flattened = None  # Otherwise Coord won't recalculate this.

        if isinstance(data, list):
            for variable in data:
                self._constrain_data(combined_mask, variable, new_coords)
                if len(variable.data) < 1:
                    return None
        else:
            self._constrain_data(combined_mask, data, new_coords)
            if len(data.data) < 1:
                return None
        return data

    def _constrain_data(self, combined_mask, data, new_coords):
        # Convert masked values to missing values
        is_masked = isinstance(data.data, np.ma.masked_array)
        if is_masked:
            missing_value = data.metadata.missing_value
            data.data = data.data.filled(fill_value=missing_value)

        # Apply the combined mask and force out the masked data
        data.data = np.ma.masked_array(data.data, mask=combined_mask)
        data.data = data.data.compressed()

        # Add the new compressed coordinates
        data._coords = new_coords