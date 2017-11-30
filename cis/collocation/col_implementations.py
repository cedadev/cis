import numpy as np
from numpy import mean as np_mean, std as np_std, min as np_min, max as np_max, sum as np_sum

import cis.exceptions
from cis.collocation.col_framework import (Constraint, PointConstraint, AbstractDataOnlyKernel)


class DummyConstraint(Constraint):
    def constrain_points(self, point, data):
        # This is a null constraint - all of the points just get passed back
        return data


class SepConstraint(PointConstraint):
    def __init__(self, h_sep=None, a_sep=None, p_sep=None, t_sep=None):
        from cis.exceptions import InvalidCommandLineOptionError

        super(SepConstraint, self).__init__()

        self.checks = []

        if h_sep is not None:
            self.h_sep = cis.utils.parse_distance_with_units_to_float_km(h_sep)
            self.checks.append(self.horizontal_constraint)
        if a_sep is not None:
            self.a_sep = cis.utils.parse_distance_with_units_to_float_m(a_sep)
            self.checks.append(self.alt_constraint)
        if p_sep is not None:
            try:
                self.p_sep = float(p_sep)
            except:
                raise InvalidCommandLineOptionError('Separation Constraint p_sep must be a valid float')
            self.checks.append(self.pressure_constraint)
        if t_sep is not None:
            from cis.parse_datetime import parse_datetimestr_delta_to_float_days
            try:
                self.t_sep = parse_datetimestr_delta_to_float_days(t_sep)
            except ValueError as e:
                raise InvalidCommandLineOptionError(e)
            self.checks.append(self.time_constraint)

    # TODO The points no longer have these methods so this will need refactoring (to work on whole DFs at a time)
    def time_constraint(self, point, ref_point):
        return point.time_sep(ref_point) < self.t_sep

    def alt_constraint(self, point, ref_point):
        return point.alt_sep(ref_point) < self.a_sep

    def pressure_constraint(self, point, ref_point):
        return point.pres_sep(ref_point) < self.p_sep

    def horizontal_constraint(self, point, ref_point):
        return point.haversine_dist(ref_point) < self.h_sep

    def constrain_points(self, ref_point, data):
        import operator
        from functools import reduce
        # Each check returns a boolean series, just || them together
        matching_points = reduce(operator.or_, [check(data, ref_point) for check in self.checks], False)
        return data[matching_points]


# noinspection PyPep8Naming
class mean(AbstractDataOnlyKernel):
    """
    Calculate mean of data points
    """

    def get_value_for_data_only(self, values):
        """
        return the mean
        """
        return np_mean(values)


# noinspection PyPep8Naming
class stddev(AbstractDataOnlyKernel):
    """
    Calculate the standard deviation
    """

    def get_value_for_data_only(self, values):
        """
        Return the standard deviation points
        """
        return np_std(values, ddof=1)


# noinspection PyPep8Naming,PyShadowingBuiltins
class min(AbstractDataOnlyKernel):
    """
    Calculate the minimum value
    """

    def get_value_for_data_only(self, values):
        """
        Return the minimum value
        """
        return np_min(values)


# noinspection PyPep8Naming,PyShadowingBuiltins
class max(AbstractDataOnlyKernel):
    """
    Calculate the maximum value
    """

    def get_value_for_data_only(self, values):
        """
        Return the maximum value
        """
        return np_max(values)


class sum(AbstractDataOnlyKernel):
    """
    Calculate the sum of the values
    """

    def get_value_for_data_only(self, values):
        """
        Return the sum of the values
        """
        return np_sum(values)


# noinspection PyPep8Naming
class moments(AbstractDataOnlyKernel):
    return_size = 3

    def __init__(self, mean_name='', stddev_name='', nopoints_name=''):
        self.mean_name = mean_name
        self.stddev_name = stddev_name
        self.nopoints_name = nopoints_name

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        """Sets name and units for mean, standard deviation and number of points variables, based
        on those of the base variable or overridden by those specified as kernel parameters.
        :param var_name: base variable name
        :param var_long_name: base variable long name
        :param var_standard_name: base variable standard name
        :param var_units: base variable units
        :return: tuple of tuples each containing (variable name, variable long name, variable units)
        """
        self.mean_name = var_name
        self.stddev_name = var_name + '_std_dev'
        stdev_long_name = 'Corrected sample standard deviation of %s' % var_long_name
        stddev_units = var_units
        self.nopoints_name = var_name + '_num_points'
        npoints_long_name = 'Number of points used to calculate the mean of %s' % var_long_name
        npoints_units = ''
        return ((self.mean_name, var_long_name, var_standard_name, var_units),
                (self.stddev_name, stdev_long_name, None, stddev_units),
                (self.nopoints_name, npoints_long_name, None, npoints_units))

    def get_value_for_data_only(self, values):
        """
        Returns the mean, standard deviation and number of values
        """

        return np_mean(values), np_std(values, ddof=1), np.size(values)


# These classes act as abbreviations for kernel classes above:


def make_coord_map(points, data):
    """
    Create a map for how coordinates from the sample points map to the standard hyperpoint coordinates. Ignoring
    coordinates which are not present in the data
    :param points: sample points
    :param data: data to map
    :return: list of tuples, each tuple is index of coordinate to use
    tuple is (hyper point coord index, sample point coord index, output coord index)
    """
    # If there are coordinates in the sample grid that are not present for the data,
    # omit the from the set of coordinates in the output grid. Find a mask of coordinates
    # that are present to use when determining the output grid shape.

    # TODO The find_standard_coords method no longer exists so I'll have to come up with another way of doing this...
    #  It should be easier using Iris coords rather than HyperPoints anyway
    coordinate_mask = [False if c is None else True for c in data.find_standard_coords()]

    # Find the mapping of standard coordinates to those in the sample points and those to be used
    # in the output data.
    # TODO


def _find_longitude_range(coords):
    """Finds the start of the longitude range, assumed to be either 0,360 or -180,180
    :param coords: coordinates to check
    :return: starting value for longitude range or None if no longitude coordinate found
    """
    low = None
    for coord in coords:
        if coord.standard_name == 'longitude':
            low = 0.0
            min_val = coord.points.min()
            if min_val < 0.0:
                low = -180.0
    return low


def _fix_longitude_range(coords, data_points):
    """Sets the longitude range of the data points to match that of the sample coordinates.
    :param coords: coordinates for grid on which to collocate
    :param data_points: HyperPointList or GriddedData of data to fix
    """
    # TODO This needs refactoring
    # FIXME this is essentially a switch on ungridded/gridded - can I do this better?
    from cis.data_io.cube_utils import set_longitude_range
    from cis.utils import fix_longitude_range
    range_start = _find_longitude_range(coords)
    if range_start is not None:
        if data_points.coords('longitude', dim_coords=True):
            set_longitude_range(data_points, range_start)
        else:
            fix_longitude_range(data_points.coord('longitude').points, range_start)

