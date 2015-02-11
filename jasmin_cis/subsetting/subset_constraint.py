from abc import ABCMeta
import logging
from collections import namedtuple

import numpy as np
import iris
import iris.coords

from jasmin_cis.subsetting.subset_framework import SubsetConstraintInterface
import jasmin_cis.data_io.gridded_data as gridded_data
from utils import guess_coord_axis


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

    def set_limit(self, coord, dim_min, dim_max):
        """
        Sets boundary values for a dimension to be used in subsetting.
        :param coord: coordinate to which limit applies
        :param dim_min: lower bound on dimension or None to indicate no lower bound
        :param dim_max: upper bound on dimension or None to indicate no upper bound
        """
        if dim_min is not None or dim_max is not None:
            logging.info("Setting limit for dimension '%s' [%s, %s]", coord.name(), str(dim_min), str(dim_max))
            self._limits[coord.name()] = CoordLimits(coord, dim_min, dim_max,
                                                     lambda x: dim_min <= x <= dim_max)

    def __str__(self):
        limit_strs = []
        for name, limit in self._limits.iteritems():
            limit_strs.append("{}: [{}, {}]".format(name, str(limit.start), str(limit.end)))
        return ', '.join(limit_strs)


class GriddedSubsetConstraint(SubsetConstraint):
    """
    Implementation of SubsetConstraint for subsetting gridded data.
    """

    def constrain(self, data):
        """
        Subsets the supplied data using a combination of iris.cube.Cube.extract and iris.cube.Cube.intersection,
        depending on whether intersection is supported (whether the coordinate has a defined modulus).
        :param data: data to be subsetted
        :return: subsetted data or None if all data excluded.
        @rtype: jasmin_cis.data_io.gridded_data.GriddedData
        """
        extract_constraint, intersection_constraint = self._make_extract_and_intersection_constraints(data)
        if extract_constraint is not None:
            data = data.extract(extract_constraint)
        if intersection_constraint:
            try:
                data = data.intersection(**intersection_constraint)
            except IndexError:
                return None
        return gridded_data.make_from_cube(data)

    def _make_extract_and_intersection_constraints(self, data):
        """
        Make the appropriate constraints:
        - dictionary of coord_name -> (min, max) for coordinates with defined modulus (to be used on the IRIS
          intersection method).
        - iris.Constraint if no defined modulus
        :param data:
        :return:
        """
        extract_constraint = None
        intersection_constraint = {}
        for coord, limits in self._limits.iteritems():
            if data.coord(coord).units.modulus is not None:
                # These coordinates can be safely used with iris.cube.Cube.intersection()
                intersection_constraint[coord] = (limits.start, limits.end)
            else:
                # These coordinates cannot be used with iris.cube.Cube.intersection(), will use iris.cube.Cube.extract()
                constraint_function = limits.constraint_function
                if extract_constraint is None:
                    extract_constraint = iris.Constraint(**{coord: constraint_function})
                else:
                    extract_constraint = extract_constraint & iris.Constraint(**{coord: constraint_function})
        return extract_constraint, intersection_constraint


class UngriddedSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting ungridded data.
    """

    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
        import numpy as np

        data = self._create_data_for_subset(data)

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

    def _create_data_for_subset(self, data):
        """
        Produce a copy of the data so that the original is not altered,
        with longitudes mapped onto the right domain for the requested limits
        :param data: Data being subsetted
        :return:
        """
        # We need a copy with new data and coordinates
        data = data.copy()
        for coord in data.coords():
            # Match user-specified limits with dimensions found in data.
            if coord.name() in self._limits:
                guessed_axis = guess_coord_axis(coord)
                if guessed_axis == 'X':
                    lon_limits = self._limits[coord.name()]
                    lon_coord = coord
                    if isinstance(lon_coord, iris.coords.Coord):
                        coord_min = lon_coord.points.min()
                        coord_max = lon_coord.points.max()
                    else:
                        coord_min = lon_coord.data.min()
                        coord_max = lon_coord.data.max()
                    data_below_zero = coord_min < 0
                    data_above_180 = coord_max > 180
                    limits_below_zero = lon_limits.start < 0 or lon_limits.end < 0
                    limits_above_180 = lon_limits.start > 180 or lon_limits.end > 180

                    if data_below_zero and not data_above_180:
                        # i.e. data is in the range -180 -> 180
                        # Only convert the data if the limits are above 180:
                        if limits_above_180 and not limits_below_zero:
                            # Convert data from -180 -> 180 to 0 -> 360
                            range_start = 0
                            coord.set_longitude_range(range_start)
                    elif data_above_180 and not data_below_zero:
                        # i.e. data is in the range 0 -> 360
                        if limits_below_zero and not limits_above_180:
                            # Convert data from 0 -> 360 to -180 -> 180
                            range_start = -180
                            coord.set_longitude_range(range_start)
                # Ensure the limits also have the new longitude coordinate
                self._limits[coord.name()].coord.data = coord.data
        return data