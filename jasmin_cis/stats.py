import abc

import numpy
import scipy.stats.mstats
from iris.cube import Cube


class StatisticsResult(object):
    """
    Holds statistical calculations performed by a statistics analysis on two files.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """

    @abc.abstractmethod
    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """


class PointsCount(StatisticsResult):
    """
    Number of points used in statistical calculation (masked or missing points excluded).
    """

    def __init__(self, num_points):
        self.num_points = num_points

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Number of points: %s" % self.num_points

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.num_points], long_name='Number of points used in calculations',  var_name='num_points')
        return cube


class DatasetMean(StatisticsResult):
    """
    Mean of an individual dataset
    """

    def __init__(self, mean, ds_name, ds_no):
        self.mean = mean
        self.ds_name = ds_name
        self.ds_no = ds_no

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Mean value of dataset %s: %s" % (self.ds_no, self.mean)

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.mean, long_name='Mean value of %s' % self.ds_name, var_name='dataset_mean_%s' % self.ds_no)


class DatasetStddev(StatisticsResult):
    """
    Standard deviations of an individual dataset
    """

    def __init__(self, stddev, ds_name, ds_no):
        self.stddev = stddev
        self.ds_name = ds_name
        self.ds_no = ds_no

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Standard deviation for dataset %s: %s" % (self.ds_no, self.stddev)

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.stddev, long_name='Corrected sample standard deviation of %s' % self.ds_name,
                    var_name='dataset_stddev_%s' % self.ds_no)


class AbsoluteMean(StatisticsResult):
    """
    Mean of the absolute difference between the two datasets (i.e, mean(data2 - data1))
    """

    def __init__(self, abs_mean):
        self.abs_mean = abs_mean

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Mean of absolute difference: %s" % self.abs_mean

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.abs_mean], long_name='Mean of the absolute difference (data2 - data1)', var_name='abs_mean')
        return cube


class AbsoluteStddev(StatisticsResult):
    """
    Standard deviation of the absolute difference between the two datasets (i.e, mean(data2 - data1))
    """

    def __init__(self, abs_stddev):
        self.abs_stddev = abs_stddev

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Standard deviation of absolute difference: %s" % self.abs_stddev

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.abs_stddev], var_name='abs_stddev',
                    long_name='Corrected sample standard deviation of the absolute difference (data2 - data1)')
        return cube


class RelativeMean(StatisticsResult):
    """
    Mean of the relative difference between the two datasets (i.e, mean((data2 - data1)/data1))
    """

    def __init__(self, rel_mean):
        self.rel_mean = rel_mean

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Mean of relative difference: %s" % self.rel_mean

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.rel_mean], long_name='Mean of the relative difference (data2 - data1)/data1',
                    var_name='rel_mean')
        return cube


class RelativeStddev(StatisticsResult):
    """
    Standard deviation of the relative difference between the two datasets (i.e, mean((data2 - data1)/data1))
    """

    def __init__(self, rel_stddev):
        self.rel_stddev = rel_stddev

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Standard deviation of relative difference: %s" % self.rel_stddev

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.rel_stddev], var_name='rel_stddev',
                    long_name='Corrected sample standard deviation of the relative difference (data2 - data1)/data1')
        return cube


class SpearmansRank(StatisticsResult):
    """
    Spearman's rank correlation coefficient
    """

    def __init__(self, spearman):
        self.spearman = spearman

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Spearman's rank coefficient: %s" % self.spearman

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.spearman], var_name='spearman', long_name="Spearman's rank correlation coefficient")
        return cube


class LinearRegressionGradient(StatisticsResult):
    """
    Linear regression gradient
    """

    def __init__(self, grad):
        self.grad = grad

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression gradient: %s" % self.grad

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.grad, long_name='Linear regression gradient', var_name='regression_gradient')


class LinearRegressionIntercept(StatisticsResult):
    """
    Linear regression intercept
    """

    def __init__(self, intercept):
        self.intercept = intercept

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression intercept: %s" % self.intercept

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.intercept, long_name='Linear regression intercept', var_name='regression_intercept')


class LinearRegressionRValue(StatisticsResult):
    """
    Linear regression r-value (PMCC)
    """

    def __init__(self, r):
        self.r = r

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression r-value: %s" % self.r

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.r, long_name='Linear regression r-value (Pearson product-moment correlation coefficient)',
                    var_name='regression_r')


class LinearRegressionPValue(StatisticsResult):
    """
    Linear regression p-value (null hypothesis)
    """

    def __init__(self, p):
        self.p = p

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression p-value: %s" % self.p

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.p, long_name='Linear regression p-value (two-sided p-value for a hypothesis '
                                      'test whose null hypothesis is that the slope is zero)', var_name='regression_p')


class LinearRegressionStderr(StatisticsResult):
    """
    Linear regression standard error of the estimate
    """

    def __init__(self, stderr):
        self.stderr = stderr

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression standard error: %s" % self.stderr

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        return Cube(self.stderr, long_name='Linear regression standard error of the estimate',
                    var_name='regression_stderr')


class StatsAnalyzer(object):
    """
    Analyse datasets to produce statistics.
    """

    def analyze(self, data1, data2,):
        """
        Perform a statistical analysis on two data sets.
        :param data1: First data object
        :param data2: Second data object
        :return: List of StatisticsResult instances.
        """
        d1, d2 = data1.data, data2.data
        grad, intercept, r, p, stderr = self.linear_regression(d1, d2)
        out = [PointsCount(self.points_count(d1, d2)),
               DatasetMean(self.mean(d1), data1.var_name, 1),
               DatasetMean(self.mean(d2), data2.var_name, 2),
               DatasetStddev(self.stddev(d1), data1.var_name, 1),
               DatasetStddev(self.stddev(d2), data2.var_name, 2),
               AbsoluteMean(self.abs_mean(d1, d2)),
               AbsoluteStddev(self.abs_stddev(d1, d2)),
               RelativeMean(self.rel_mean(d1, d2)),
               RelativeStddev(self.rel_stddev(d1, d2)),
               SpearmansRank(self.spearmans_rank(d1, d2)),
               LinearRegressionGradient(grad),
               LinearRegressionIntercept(intercept),
               LinearRegressionRValue(r),
               LinearRegressionPValue(p),
               LinearRegressionStderr(stderr)]
        return out

    def points_count(self, data1, data2):
        """
        Count all points which will be used for statistical comparison operations
        (i.e. are non-missing in both datasets).
        :param data1:
        :param data2:
        :return:
        """
        return numpy.ma.count(data1 + data2)

    def mean(self, data):
        """
        Mean of a dataset
        :param data:
        :return:
        """
        return numpy.mean(data)

    def stddev(self, data):
        """
        Corrected sample standard deviation of dataset
        :param data:
        :return:
        """
        return numpy.std(data, ddof=1)

    def abs_mean(self, data1, data2):
        """
        Mean of absolute difference d2-d1
        :param data1:
        :param data2:
        :return:
        """
        return numpy.mean(data2 - data1)

    def abs_stddev(self, data1, data2):
        """
        Standard deviation of absolute difference d2-d1
        :param data1:
        :param data2:
        :return:
        """
        return numpy.std(data2 - data1, ddof=1)

    def rel_mean(self, data1, data2):
        """
        Mean of relative difference (d2-d1)/d1
        :param data1:
        :param data2:
        :return:
        """
        return numpy.mean((data2 - data1)/data1)

    def rel_stddev(self, data1, data2):
        """
        Mean of relative difference (d2-d1)/d1
        :param data1:
        :param data2:
        :return:
        """
        return numpy.std((data2 - data1)/data1, ddof=1)

    def spearmans_rank(self, data1, data2):
        """
        Perform a spearmans rank on the data
        :param data1:
        :param data2:
        :return:
        """
        return scipy.stats.mstats.spearmanr(data1, data2, None)[0]

    def linear_regression(self, data1, data2):
        """
        Perform a linear regression on the data
        :param data1:
        :param data2:
        :return:
        """
        return scipy.stats.mstats.linregress(data1, data2)
