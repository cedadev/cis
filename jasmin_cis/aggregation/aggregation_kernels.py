import iris.analysis
from numpy import ma, zeros


class StddevKernel(iris.analysis.Aggregator):
    """
    Custom standard deviation kernel (to allow calculation of standard deviation with appropriate metadata).
    """
    def __init__(self):
        super(StddevKernel, self).__init__('standard_deviation', ma.std, ddof=1)

    def update_metadata(self, cube, coords, **kwargs):
        """
        Update cube metadata after aggregation
        """
        super(StddevKernel, self).update_metadata(cube, coords, **kwargs)
        cube.standard_name = None
        cube.long_name = 'Corrected sample standard deviation of {long_name}'.format(long_name=cube.long_name)
        cube.var_name = '{var_name}_std_dev'.format(var_name=cube.var_name)


class CountKernel(iris.analysis.Aggregator):
    """
    Custom counting kernel (to allow calculation of the number of points used in an aggregation cell,
    with appropriate metadata).
    """
    def __init__(self):
        super(CountKernel, self).__init__('count', self.count_kernel_func)

    @staticmethod
    def count_kernel_func(data, axis, **kwargs):
        """
        Count the number of (non-masked) points used in the aggregation for this cell.
        """
        if not ma.isMaskedArray(data):
            data = ma.masked_array(data, zeros(data.shape))
        return data.count(axis)

    def update_metadata(self, cube, coords, **kwargs):
        """
        Update cube metadata after aggregation
        """
        super(CountKernel, self).update_metadata(cube, coords, **kwargs)
        cube.standard_name = None
        cube.long_name = 'Number of points used to calculate the mean of {long_name}'.format(long_name=cube.long_name)
        cube.var_name = '{var_name}_num_points'.format(var_name=cube.var_name)
        cube.units = None


class MultiKernel(object):
    """
    Represents a set of kernels to be applied each in turn
    """
    def __init__(self, cell_method, sub_kernels):
        """
        Create a new MultiKernel
        :param cell_method: String name for the kernel
        :param sub_kernels: List of kernels to be applied each in turn
        :return: MultiKernel
        """
        self.cell_method = cell_method
        self.sub_kernels = sub_kernels


aggregation_kernels = {'mean': iris.analysis.MEAN,
                       'min': iris.analysis.MIN,
                       'max': iris.analysis.MAX,
                       'moments': MultiKernel('moments', [iris.analysis.MEAN, StddevKernel(), CountKernel()])}