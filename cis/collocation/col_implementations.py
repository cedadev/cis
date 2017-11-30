import numpy as np
from numpy import mean as np_mean, std as np_std, min as np_min, max as np_max, sum as np_sum

from cis.collocation.col_framework import (AbstractDataOnlyKernel)


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


def find_standard_coords(data):
    """Constructs a list of the standard coordinates.
    The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
    list in this order.
    :return: list of coordinates or None if coordinate not present
    """
    ret_list = []

    coords = data.coords(dim_coords=True)
    for name in HyperPoint.standard_names:
        coord_and_dim = None
        for idx, coord in enumerate(coords):
            if coord.standard_name == name:
                coord_and_dim = (coord, idx)
                break
        ret_list.append(coord_and_dim)

    return ret_list


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

    coordinate_mask = [False if c is None else True for c in find_standard_coords(data)]

    # Find the mapping of standard coordinates to those in the sample points and those to be used
    # in the output data.
    # TODO
    # Find the mapping of standard coordinates to those in the sample points and those to be used
    # in the output data.
    return _find_standard_coords(points, coordinate_mask)


def _find_standard_coords(cube, coordinate_mask):
    """Finds the mapping of sample point coordinates to the standard ones used by HyperPoint.

    :param cube: cube among the coordinates of which to find the standard coordinates
    :param coordinate_mask: list of booleans indicating HyperPoint coordinates that are present
    :return: list of tuples relating index in HyperPoint to index in coords and in coords to be iterated over
    """
    coord_map = []
    cube_coord_lookup = {}

    cube_coords = cube.coords()
    for idx, coord in enumerate(cube_coords):
        cube_coord_lookup[coord] = idx

    shape_idx = 0
    for hpi, name in enumerate(HyperPoint.standard_names):
        if coordinate_mask[hpi]:
            # Get the dimension coordinates only - these correspond to dimensions of data array.
            cube_coords = cube.coords(standard_name=name, dim_coords=True)
            if len(cube_coords) > 1:
                msg = ('Expected to find exactly 1 coordinate, but found %d. They were: %s.'
                       % (len(cube_coords), ', '.join(coord.name() for coord in cube_coords)))
                raise cis.exceptions.CoordinateNotFoundError(msg)
            elif len(cube_coords) == 1:
                coord_map.append((hpi, cube_coord_lookup[cube_coords[0]], shape_idx))
                shape_idx += 1
    return coord_map