from abc import ABCMeta, abstractmethod
import six
import logging

import numpy as np
import iris
import iris.coords

import cis.data_io.cube_utils as gridded_data


def subset(data, **kwargs):
    """
    Helper function for constraining a CommonData or CommonDataList object (data) given a SubsetConstraint
    class, the constraints should be specified using the kwargs of the form coord: [min, max]

    A shape keyword can also be supplied as a WKT string or shapely object to subset in lat/lon by an arbitrary shape.

    :param CommonData or CommonDataList data: The data to subset
    :param class SubsetConstraint constraint: A SubsetConstraint class to do the constraining
    :param kwargs: The limits as slices or length 2 tuples of max and min.
    :return:
    """
    from datetime import datetime
    from cis.time_util import PartialDateTime
    from cis.exceptions import CoordinateNotFoundError
    from shapely.wkt import loads
    from shapely.geos import ReadingError
    from cis.data_io.cube_utils import _get_coord

    constraints = {}

    for dim_name, limit in kwargs.items():
        # Deal with shape argument
        if dim_name == 'shape':
            if isinstance(limit, six.string_types):
                try:
                    shape = loads(limit)
                except ReadingError:
                    raise ValueError("Invalid shape string: " + limit)
            else:
                shape = limit
            constraints['shape'] = shape
            bounding_box = shape.bounds
            # Create the lat/lon box - this will be used to speed up the shape subset
            constraints[data.coord(standard_name='longitude').name()] = slice(bounding_box[0], bounding_box[2])
            constraints[data.coord(standard_name='latitude').name()] = slice(bounding_box[1], bounding_box[3])
            continue

        c = _get_coord(data, dim_name)
        if c is None:
            raise CoordinateNotFoundError("No coordinate found that matches '{}'. Please check the "
                                          "coordinate name.".format(dim_name))

        if all(hasattr(limit, att) for att in ('start', 'stop')):
            l = limit
        elif isinstance(limit, PartialDateTime):
            l = slice(c.units.date2num(limit.min()),
                      c.units.date2num(limit.max()))
        elif len(limit) == 1 and isinstance(limit[0], PartialDateTime):
            l = slice(c.units.date2num(limit[0].min()),
                      c.units.date2num(limit[0].max()))
        elif len(limit) == 2:
            l = slice(limit[0], limit[1])
        else:
            raise ValueError("Invalid subset arguments: {}".format(limit))

        # Fill in defaults and convert datetimes
        limit_start = l.start if l.start is not None else c.points.min()
        if isinstance(limit_start, datetime):
            limit_start = c.units.date2num(limit_start)

        limit_end = l.stop if l.stop is not None else c.points.max()
        if isinstance(limit_end, datetime):
            limit_end = c.units.date2num(limit_end)
        constraints[_get_coord(data, dim_name).name()] = slice(limit_start, limit_end)

    subset_constraint = GriddedSubsetConstraint(constraints)

    subset = subset_constraint.constrain(data)

    if subset is not None:
        subset.add_history("Subsetted using limits: " + str(subset_constraint))

    return subset


@six.add_metaclass(ABCMeta)
class SubsetConstraint(object):
    """Abstract Constraint for subsetting.

    Holds the limits for subsetting in each dimension.
    """

    def __init__(self, limits, shape=None):
        """
        :param dict limits: A dictionary mapping coordinate name to slice objects
        """
        self._limits = limits
        self._shape = shape
        logging.debug("Created SubsetConstraint of type %s", self.__class__.__name__)

    def __str__(self):
        limit_strs = []
        for name, limit in self._limits.items():
            limit_strs.append("{}: [{}, {}]".format(name, str(limit.start), str(limit.stop)))
        return ', '.join(limit_strs)

    @abstractmethod
    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """


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
        _shape = self._limits.pop('shape', None)
        extract_constraint, intersection_constraint = self._make_extract_and_intersection_constraints(data)
        # TODO this doesn't deal with Multi-dimensional coordinates
        if extract_constraint is not None:
            data = data.extract(extract_constraint)
            if data is None:
                return None  # Don't do the intersection
        if intersection_constraint:
            try:
                data = data.intersection(**intersection_constraint)
            except IndexError:
                return None

        if _shape is not None:
            if data.ndim > 2:
                raise NotImplementedError("Unable to perform shape subset for multidimensional gridded datasets")
            mask = np.ones(data.shape, dtype=bool)
            mask[np.unravel_index(_get_gridded_subset_region_indices(data, _shape), data.shape)] = False
            if isinstance(data.data, np.ma.MaskedArray):
                data.data.mask &= mask
            else:
                data.data = np.ma.masked_array(data.data, mask)
        return data

    def _make_extract_and_intersection_constraints(self, data):
        """
        Make the appropriate constraints:
        - dictionary of coord_name -> (min, max) for coordinates with defined modulus (to be used on the IRIS
          intersection method).
        - iris.Constraint if no defined modulus
        :param data:
        :return:
        """
        class Contains(object):
            """
            Callable object for checking if a value is within a preset range
            """
            def __init__(self, lower, upper):
                self.lower = lower
                self.upper = upper

            def __call__(self, x):
                return self.lower <= x.point <= self.upper

        intersection_constraint = {}
        extract_constraint = iris.Constraint()
        for coord, limits in self._limits.items():
            if data.coord(coord).units.modulus is not None:
                # These coordinates can be safely used with iris.cube.Cube.intersection()
                intersection_constraint[coord] = (limits.start, limits.stop)
            else:
                # These coordinates cannot be used with iris.cube.Cube.intersection(), will use iris.cube.Cube.extract()
                extract_constraint = extract_constraint & iris.Constraint(**{coord: Contains(limits.start, limits.stop)})
        return extract_constraint, intersection_constraint


def _get_indices_for_lat_lon_points(lats, lons, region):
    from shapely.geometry import MultiPoint

    lat_lon_points = np.vstack([lats, lons])
    points = MultiPoint(lat_lon_points.T)

    # Performance in this loop might be an issue, but I think it's essentially how GeoPandas does it. If I want to
    #  improve it I might need to look at using something like rtree.
    return [i for i, p in enumerate(points) if region.contains(p)]


def _get_ungridded_subset_region_indices(ungridded_data, region):
    # We have to use flatten rather than flat, GEOS creates a copy of the data if it's a view anyway.
    return _get_indices_for_lat_lon_points(ungridded_data.lon.data.flatten(), ungridded_data.lat.data.flatten(), region)


def _get_gridded_subset_region_indices(gridded_data, region):
    # Using X and Y is a bit more general than lat and lon - the shapefiles needn't actually represent lat/lon
    x, y = np.meshgrid(gridded_data.coord(axis='X').points, gridded_data.coord(axis='Y').points)
    return _get_indices_for_lat_lon_points(x.flat, y.flat, region)
