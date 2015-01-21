import abc

from iris.cube import Cube
from iris.coords import AuxCoord


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


class DatasetMeans(StatisticsResult):
    """
    Means of each dataset individually
    """

    def __init__(self, mean1, mean2, dsname1, dsname2):
        self.means = (mean1, mean2)
        self.dsnames = (dsname1, dsname2)

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Dataset means: %s, %s" % self.means

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        dim = AuxCoord(self.dsnames, long_name='Input datasets', var_name='datasets')
        cube = Cube(self.means, long_name='Mean value of each dataset', var_name='dataset_means',
                    aux_coords_and_dims=[(dim, 0)])
        return cube


class DatasetStddevs(StatisticsResult):
    """
    Standard deviations of each object individually
    """

    def __init__(self, stddev1, stddev2, dsname1, dsname2):
        self.stddevs = (stddev1, stddev2)
        self.dsnames = (dsname1, dsname2)

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Dataset standard deviations: %s, %s" % self.stddevs

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        dim = AuxCoord(self.dsnames, long_name='Input datasets', var_name='datasets')
        cube = Cube(self.stddevs, long_name='Unbiased standard deviation of each dataset', var_name='dataset_stddevs',
                    aux_coords_and_dims=[(dim, 0)])
        return cube


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
                    long_name='Unbiased standard deviation of the absolute difference (data2 - data1)')
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
                    long_name='Unbiased standard deviation of the relative difference (data2 - data1)/data1')
        return cube


class PearsonCorrelation(StatisticsResult):
    """
    The Pearson product-moment correlation coefficient
    """

    def __init__(self, pearson):
        self.pearson = pearson

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Pearson coefficient: %s" % self.pearson

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        cube = Cube([self.pearson], var_name='pearson', long_name="Pearson product-moment correlation coefficient")
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
        cube = Cube([self.spearman], var_name='spearmans', long_name="Spearman's rank correlation coefficient")
        return cube


class LinearRegression(StatisticsResult):
    """
    Linear regression results
    """

    def __init__(self, a, b, r, pval, stderr):
        self.regression = (a, b, r, pval, stderr)

    def pprint(self):
        """
        Nicely formatted string representation of this statistical result, suitable for printing to screen.
        """
        return "Linear regression results: data2 = %s x data1 + %s;" \
               " r-value: %s; p-value: %s; stderr: %s" % self.regression

    def as_cube(self):
        """
        Get this statistical result as an iris.cube.Cube instance
        """
        from iris.coords import AuxCoord
        dim = AuxCoord(['gradient', 'intercept', 'r-value', 'p-value', 'stderr'],
                       long_name='Linear regression results components', var_name='regression_components')
        cube = Cube(self.regression, long_name='Linear regression results', var_name='regression',
                    aux_coords_and_dims=[(dim, 0)])
        return cube
