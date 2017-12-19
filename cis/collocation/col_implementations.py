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

