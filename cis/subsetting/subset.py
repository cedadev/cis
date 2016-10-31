from abc import ABCMeta
import logging

import numpy as np
import iris
import iris.coords

from cis.subsetting.subset_framework import SubsetConstraintInterface
import cis.data_io.gridded_data as gridded_data


def subset(data, constraint, **kwargs):
    """
    Helper function for constraining a CommonData or CommonDataList object (data) given a SubsetConstraintInterface
    object, the constraints should be specified using the kwargs of the form coord: [min, max]

    :param CommonData or CommonDataList data:
    :param SubsetConstraintInterface constraint:
    :param kwargs:
    :return:
    """
    from datetime import datetime
    from cis.time_util import PartialDateTime
    from cis.exceptions import CoordinateNotFoundError

    constraints = {}

    for dim_name, limit in kwargs.items():
        c = data._get_coord(dim_name)
        if c is None:
            raise CoordinateNotFoundError("No coordinate found that matches '{}'. Please check the "
                                          "coordinate name.".format(dim_name))

        if all(hasattr(limit, att) for att in ('start', 'stop')):
            l = limit
        elif len(limit) == 1 and isinstance(limit[0], PartialDateTime):
            l = slice(_convert_datetime_to_coord_unit(c, limit[0].min()),
                      _convert_datetime_to_coord_unit(c, limit[0].max()))
        elif len(limit) == 2:
            if isinstance(limit[0], datetime) and isinstance(limit[1], datetime):
                # Ensure that the limits are date/times.
                limit_start = _convert_datetime_to_coord_unit(c, limit[0])
                limit_end = _convert_datetime_to_coord_unit(c, limit[1])
            else:
                # Assume to be a non-time axis.
                limit_start, limit_end = _fix_non_circular_limits(limit[0], limit[1])
            l = slice(limit_start, limit_end)
        else:
            raise ValueError("Invalid subset arguments: {}".format(limit))
        constraints[data._get_coord(dim_name).name()] = l

    subset_constraint = constraint(constraints)

    subset = subset_constraint.constrain(data)

    if subset is not None:
        subset.add_history("Subsetted using limits: " + str(subset_constraint))

    return subset


def _convert_datetime_to_coord_unit(coord, dt):
    """Converts a datetime to be in the unit of a specified Coord.
    """
    from cf_units import Unit

    if isinstance(coord, iris.coords.Coord):
        # The unit class is then cf_units.Unit.
        iris_unit = coord.units
    else:
        iris_unit = Unit(coord.units)
    return iris_unit.date2num(dt)


def _fix_non_circular_limits(limit_start, limit_end):
    if limit_start <= limit_end:
        new_limits = (limit_start, limit_end)
    else:
        new_limits = (limit_end, limit_start)
        logging.info("Real limits: original: %s  after fix: %s", (limit_start, limit_end), new_limits)

    return new_limits


class SubsetConstraint(SubsetConstraintInterface):
    """Abstract Constraint for subsetting.

    Holds the limits for subsetting in each dimension.

    """
    __metaclass__ = ABCMeta

    def __init__(self, limits):
        # TODO: Document what these limits should be...
        self._limits = limits
        logging.debug("Created SubsetConstraint of type %s", self.__class__.__name__)

    def __str__(self):
        limit_strs = []
        for name, limit in self._limits.items():
            limit_strs.append("{}: [{}, {}]".format(name, str(limit.start), str(limit.stop)))
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
        @rtype: cis.data_io.gridded_data.GriddedData
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
        for coord, limits in self._limits.items():
            if data.coord(coord).units.modulus is not None:
                # These coordinates can be safely used with iris.cube.Cube.intersection()
                intersection_constraint[coord] = (limits.start, limits.stop)
            else:
                # These coordinates cannot be used with iris.cube.Cube.intersection(), will use iris.cube.Cube.extract()
                constraint_function = lambda x: limits.start <= x.point <= limits.stop
                if extract_constraint is None:
                    extract_constraint = iris.Constraint(**{coord: constraint_function})
                else:
                    extract_constraint = extract_constraint & iris.Constraint(**{coord: constraint_function})
        return extract_constraint, intersection_constraint


class UngriddedSubsetConstraint(SubsetConstraint):
    """Implementation of SubsetConstraint for subsetting ungridded data.

    .. Note:
        The constrain method is not used for ungridded subsetting which uses fixed numpy comparisons for speed.

    """

    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
        import numpy as np
        from cis.utils import listify

        data = self._create_data_for_subset(data)

        # Create the combined mask across all limits
        shape = data.coords()[0].data_flattened.shape  # This assumes they are all the same shape
        combined_mask = np.zeros(shape, dtype=bool)
        for coord, limit in self._limits.items():
            # Mask out any points which are NOT (<= to the end limit AND >= to the start limit)
            mask = ~ (np.less_equal(data.coord(coord).data_flattened, limit.stop) &
                      np.greater_equal(data.coord(coord).data_flattened, limit.start))
            combined_mask = combined_mask | mask

        # Generate the new coordinates here (before we loop)
        new_coords = data.coords()
        for coord in new_coords:
            coord.data = np.ma.masked_array(coord.data, mask=combined_mask)
            coord.data = coord.data.compressed()
            coord.metadata.shape = coord.data.shape
            coord._data_flattened = None  # Otherwise Coord won't recalculate this.

        for variable in listify(data):
            # Constrain each copy of the data object in-place
            self._constrain_data(combined_mask, variable, new_coords)
            # If any of the data objects are None then they all must be - so return None
            if len(variable.data) < 1:
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
        # Check for longitude coordinate in the limits
        for dim_name, limit in self._limits.items():
            coord = data.coord(dim_name)
            if coord.standard_name == 'longitude':
                coord_min = coord.points.min()
                coord_max = coord.points.max()
                data_below_zero = coord_min < 0
                data_above_180 = coord_max > 180
                limits_below_zero = limit.start < 0 or limit.stop < 0
                limits_above_180 = limit.start > 180 or limit.stop > 180

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
        return data
