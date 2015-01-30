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

    def __init__(self, data1, data2):
        """
        Create a statistics analyser for two data sets
        :param data1: First data object
        :param data2: Second data object
        :return: List of StatisticsResult instances.
        """

        self.data1 = data1
        self.data2 = data2

    def analyze(self):
        """
        Perform a statistical analysis on two data sets.
        :return: List of StatisticsResult instances.
        """
        out = []
        out.extend(self.points_count())
        out.extend(self.means())
        out.extend(self.stddevs())
        out.extend(self.abs_mean())
        out.extend(self.abs_stddev())
        out.extend(self.rel_mean())
        out.extend(self.rel_stddev())
        out.extend(self.spearmans_rank())
        out.extend(self.linear_regression())
        return out

    def points_count(self):
        """
        Count all points which will be used for statistical comparison operations
        (i.e. are non-missing in both datasets).
        :return: List of StatisticsResults
        """
        count = numpy.ma.count(self.data1.data + self.data2.data)
        return [PointsCount(count)]

    def means(self):
        """
        Means of two datasets
        :return: List of StatisticsResults
        """

        return [DatasetMean(numpy.mean(self.data1.data), self.data1.var_name, 1),
                DatasetMean(numpy.mean(self.data2.data), self.data2.var_name, 2)]

    def stddevs(self):
        """
        Corrected sample standard deviation of datasets
        :return: List of StatisticsResults
        """
        return [DatasetStddev(numpy.std(self.data1.data, ddof=1), self.data1.var_name, 1),
                DatasetStddev(numpy.std(self.data2.data, ddof=1), self.data2.var_name, 2)]

    def abs_mean(self):
        """
        Mean of absolute difference d2-d1
        :return: List of StatisticsResults
        """
        mean = numpy.mean(self.data2.data - self.data1.data)
        return [AbsoluteMean(mean)]

    def abs_stddev(self):
        """
        Standard deviation of absolute difference d2-d1
        :return: List of StatisticsResults
        """
        stddev = numpy.std(self.data2.data - self.data1.data, ddof=1)
        return [AbsoluteStddev(stddev)]

    def rel_mean(self):
        """
        Mean of relative difference (d2-d1)/d1
        :return: List of StatisticsResults
        """
        mean = numpy.mean((self.data2.data - self.data1.data)/self.data1.data)
        return [RelativeMean(mean)]

    def rel_stddev(self):
        """
        Mean of relative difference (d2-d1)/d1
        :return: List of StatisticsResults
        """
        stddev = numpy.std((self.data2.data - self.data1.data)/self.data1.data, ddof=1)
        return [RelativeStddev(stddev)]

    def spearmans_rank(self):
        """
        Perform a spearman's rank on the data
        :return: List of StatisticsResults
        """
        spearman = scipy.stats.mstats.spearmanr(self.data1.data, self.data2.data, None)[0]
        return [SpearmansRank(spearman)]

    def linear_regression(self):
        """
        Perform a linear regression on the data
        :return: List of StatisticsResults
        """
        grad, intercept, r, p, stderr = scipy.stats.mstats.linregress(self.data1.data, self.data2.data)
        return [LinearRegressionGradient(grad),
                LinearRegressionIntercept(intercept),
                LinearRegressionRValue(r),
                LinearRegressionStderr(stderr)]
