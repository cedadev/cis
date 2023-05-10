from abc import ABCMeta, abstractmethod
import six
import logging

import numpy as np
import iris
import iris.coords

import cis.data_io.gridded_data as gridded_data


def subset(data, constraint, **kwargs):
    """
    Helper function for constraining a CommonData or CommonDataList object (data) given a SubsetConstraint
    class, the constraints should be specified using the kwargs of the form coord: [min, max]

    A shape keyword can also be supplied as a WKT string or shapely object to subset in lat/lon by an arbitrary shape.

    :param CommonData or CommonDataList data: The data to subset
    :param class SubsetConstraint constraint: A SubsetConstraint class to do the constraining
    :param kwargs: The limits as slices or length 2 tuples of max and min.
    :return:
    """
    from cis.time_util import PartialDateTime
    from cis.exceptions import CoordinateNotFoundError
    from shapely.wkt import loads

    constraints = {}

    for dim_name, limit in kwargs.items():
        # Deal with shape argument
        if dim_name == 'shape':
            if isinstance(limit, six.string_types):
                try:
                    shape = loads(limit)
                except Exception:
                    raise ValueError("Invalid shape string: " + limit)
            else:
                shape = limit
            constraints['shape'] = shape
            bounding_box = shape.bounds
            # Create the lat/lon box - this will be used to speed up the shape subset
            constraints[data.coord(standard_name='longitude').name()] = slice(bounding_box[0], bounding_box[2])
            constraints[data.coord(standard_name='latitude').name()] = slice(bounding_box[1], bounding_box[3])
            continue

        c = data._get_coord(dim_name)
        if c is None:
            raise CoordinateNotFoundError("No coordinate found that matches '{}'. Please check the "
                                          "coordinate name.".format(dim_name))

        if all(hasattr(limit, att) for att in ('start', 'stop')):
            l = limit
        elif isinstance(limit, PartialDateTime):
            l = slice(limit.min(), limit.max())
        elif len(limit) == 1 and isinstance(limit[0], PartialDateTime):
            l = slice(limit[0].min(), limit[0].max())
        elif len(limit) == 2:
            l = slice(limit[0], limit[1])
        else:
            raise ValueError("Invalid subset arguments: {}".format(limit))

        # Fill in defaults
        limit_start = l.start if l.start is not None else c.points.min()
        limit_end = l.stop if l.stop is not None else c.points.max()

        constraints[data._get_coord(dim_name).name()] = slice(limit_start, limit_end)

    subset_constraint = constraint(constraints)

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


class UngriddedSubsetConstraint(SubsetConstraint):
    """
    Implementation of SubsetConstraint for subsetting ungridded data.
    """
    def __init__(self, limits):
        super(UngriddedSubsetConstraint, self).__init__(limits)
        self._shape_indices = None
        self._combined_mask = None

    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
        import numpy as np
        from datetime import datetime
        from cis.data_io.ungridded_data import UngriddedDataList

        if isinstance(data, list):
            # Calculating masks and indices will only take place on the first iteration,
            # so we can just call this method recursively if we've got a list of data.
            output = UngriddedDataList()
            for var in data:
                output.append(self.constrain(var))
            return output

        _data = self._create_data_for_subset(data)

        _shape = self._limits.pop('shape', None)

        if self._combined_mask is None:
            # Create the combined mask across all limits
            shape = _data.coords()[0].data.shape  # This assumes they are all the same shape
            combined_mask = np.ones(shape, dtype=bool)
            for coord, limit in self._limits.items():
                # Convert the points to datetimes if the limit is a datetime
                if isinstance(limit.start, datetime):
                    points = _data.coord(coord).units.num2date(_data.coord(coord).data)
                else:
                    points = _data.coord(coord).data
                # Select any points which are <= to the stop limit AND >= to the start limit
                mask = (np.less_equal(points, limit.stop) & np.greater_equal(points, limit.start))
                combined_mask &= mask
            self._combined_mask = combined_mask

        _data = _data[self._combined_mask]

        if _shape is not None:
            if self._shape_indices is None:
                self._shape_indices = _get_ungridded_subset_region_indices(_data, _shape)
            _data = _data[np.unravel_index(self._shape_indices, _data.shape)]

        if _data.size == 0:
            _data = None

        return _data

    def _create_data_for_subset(self, data):
        """
        Produce a copy of the data so that the original is not altered,
        with longitudes mapped onto the right domain for the requested limits
        :param data: Data being subsetted
        :return:
        """
        from cis.exceptions import CoordinateNotFoundError
        # We need a copy with new data and coordinates
        data = data.copy()
        # Check for longitude coordinate in the limits
        for dim_name, limit in self._limits.items():
            try:
                coord = data.coord(dim_name)
            except CoordinateNotFoundError:
                # E.g. shape...
                continue
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


def _get_indices_for_lat_lon_points(lats, lons, region):
    from shapely.geometry import MultiPoint

    lat_lon_points = np.vstack([lats, lons])
    points = MultiPoint(lat_lon_points.T)

    # Performance in this loop might be an issue, but I think it's essentially how GeoPandas does it. If I want to
    #  improve it I might need to look at using something like rtree.
    return [i for i, p in enumerate(points.geoms) if region.contains(p)]


def _get_ungridded_subset_region_indices(ungridded_data, region):
    # We have to use flatten rather than flat, GEOS creates a copy of the data if it's a view anyway.
    return _get_indices_for_lat_lon_points(ungridded_data.lon.data.flatten(), ungridded_data.lat.data.flatten(), region)


def _get_gridded_subset_region_indices(gridded_data, region):
    # Using X and Y is a bit more general than lat and lon - the shapefiles needn't actually represent lat/lon
    x, y = np.meshgrid(gridded_data.coord(axis='X').points, gridded_data.coord(axis='Y').points)
    return _get_indices_for_lat_lon_points(x.flat, y.flat, region)
