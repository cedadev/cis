from abc import ABCMeta, abstractmethod
import six
from cis.utils import index_iterator_for_non_masked_data, index_iterator_nditer
import numpy as np


@six.add_metaclass(ABCMeta)
class Collocator(object):
    """
    Class which provides a method for performing collocation. This just defines the interface which
    the subclasses must implement.
    """
    def __init__(self, fill_value=None, var_name='', var_long_name='', var_units='',
                 missing_data_for_missing_sample=False):
        """
        Initialise the fill_value, missing data flag and variable attributes.

        :param fill_value: The value to use when the kernel is unable to return a value. The default is NaN.
        :param var_name: The name of the variable to use when creating the output data object
        :param var_long_name: The long name of the variable to use when creating the output data object
        :param var_units: The units of the variable to use when creating the output data object
        :param missing_data_for_missing_sample: If True then sample points which have a missing value will result in
         data points with a missing value - regardless of the collocation result. The default is False.
        :return:
        """
        self.fill_value = float(fill_value) if fill_value is not None else np.nan
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units
        self.missing_data_for_missing_sample = missing_data_for_missing_sample

    @abstractmethod
    def collocate(self, points, data, constraint, kernel):
        """
        The method is responsible for setting up and running the collocation. It should take a set of data and map that
        onto the given (sample) points using the constraint and kernel provided.

        :param points: A set of sample points onto which we will collocate some other 'data'
        :param data: Some other data to be collocated onto the 'points'
        :param constraint: A :class:`.Constraint` instance which provides a :meth:`.Constraint.constrain_points` method,
         and optionally an :meth:`.Constraint.get_iterator` method
        :param kernel: A :class:`.Kernel` instance which provides a :meth:`.Kernel.get_value` method
        :return: One or more :class:`.CommonData` (or subclasses of) objects whose coordinates lie on the points
         defined above.
        """


class Kernel(object):
    """
    Class which provides a method for taking a number of points and returning one value. For example a nearest
    neighbour algorithm or sort algorithm or mean. This just defines the interface which the subclasses must implement.
    """
    __metaclass__ = ABCMeta

    #: The number of values the :meth:`.Kernel.get_value` should be expected to return
    #: (i.e. the length of the return list).
    return_size = 1

    @abstractmethod
    def get_value(self, point, data):
        """
        This method should return a single value (if :attr:`.Kernel.return_size` is 1) or a list of n values (if
        :attr:`.Kernel.return_size` is n) based on some calculation on the data given a single point.

        The data is deliberately left unspecified in the interface as it may be any type of data, however it is expected
        that each implementation will only work with a specific type of data (gridded, ungridded etc.) Note that this
        method will be called for every sample point and so could become a bottleneck for calculations, it is advisable
        to make it as quick as is practical. If this method is unable to provide a value (for example if no data points
        were given) a ValueError should be thrown.

        :param point: A single HyperPoint
        :param data: A set of data points to reduce to a single value
        :return: For return_size=1 a single value (number) otherwise a list of return values, which represents some
            operation on the points provided
        :raises ValueError: When the method is unable to return a value
        """

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        """Returns the details of all variables to be created from the outputs of a kernel.

        :param str var_name: Base variable name
        :param str var_long_name: Base variable long name
        :param str var_standard_name: Base variable standard_name
        :param str var_units: Base variable units
        :return: Tuple of tuples, each containing (variable name, variable long name, variable units)
        """
        return ((var_name, var_long_name, var_standard_name, var_units), )


class AbstractDataOnlyKernel(Kernel):
    """
    A Kernel that can work on data only, e.g. mean only requires the data values to calculate the mean, not the sampling
    point.
    """

    __metaclass__ = ABCMeta

    def get_value(self, point, data):
        """
        This method is redundant in the AbstractDataOnlyKernel and only serves as an interface to
        :meth:`.AbstractDataOnlyKernel`, removing the unnecessary point and checking for one or more data points.

        :param point: A single HyperPoint
        :param data: A set of data points to reduce to a single value
        :return: For return_size=1 a single value (number) otherwise a list of returns values, which represents some
            operation on the points provided
        """
        values = data.vals
        if len(values) == 0:
            raise ValueError
        return self.get_value_for_data_only(values)


    @abstractmethod
    def get_value_for_data_only(self, values):
        """
        This method should return a single value (if :attr:`.Kernel.return_size` is 1) or a list of n values
        (if :attr:`.Kernel.return_size` is n) based on some calculation on the the values (a numpy array).

        Note that this method will be called for every sample point in which data can be placed and so could become a
        bottleneck for calculations, it is advisable to make it as quick as is practical. If this method is unable to
        provide a value (for example if no data points were given) a ValueError should be thrown. This method will not
        be called if there are no values to be used for calculations.

        :param values: A numpy array of values (can not be none or empty)
        :return: A single data item if return_size is 1 or a list of items containing :attr:`.Kernel.return_size` items
        :raises ValueError: If there are any problems creating a value
        """


class Constraint(object):
    """
    Class which provides a method for constraining a set of points. A single HyperPoint is given as a reference
    but the data points to be reduced ultimately may be of any type. This just defines the interface which the
    subclasses must implement.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def constrain_points(self, point, data):
        """
        This method should return a subset of the data given a single reference point.
        It is expected that the data returned should be of the same type as that given - but this isn't mandatory. It is
        possible that this function will return zero points (no data), the collocation class is responsible for
        providing a fill_value.

        :param HyperPoint point: A single HyperPoint
        :param data: A set of data points to be reduced
        :return: A reduced set of data points
        """

    def get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data):
        """
        Iterator to iterate through the points needed to be calculated.
        The default iterator, iterates through all the sample points calling :meth:`.Constraint.constrain_points` for
        each one.

        :param missing_data_for_missing_sample: If true anywhere there is missing data on the sample then final point is
         missing; otherwise just use the sample
        :param coord_map: Coordinate map - list of tuples of indexes of hyperpoint coord, data coords and output coords
        :param coords: The coordinates to map the data onto
        :param data_points: The (non-masked) data points
        :param shape: Shape of the final data values
        :param points: The original points object, these are the points to collocate
        :param output_data: Output data set
        :return: Iterator which iterates through (sample indices, hyper point and constrained points) to be placed in
         these points
        """
        from cis.collocation.col_implementations import HyperPoint
        if missing_data_for_missing_sample:
            iterator = index_iterator_for_non_masked_data(shape, points)
        else:
            iterator = index_iterator_nditer(shape, output_data[0])

        for indices in iterator:
            hp_values = [None] * HyperPoint.number_standard_names
            for (hpi, ci, shi) in coord_map:
                hp_values[hpi] = coords[ci].points[indices[shi]]

            hp = HyperPoint(*hp_values)
            constrained_points = self.constrain_points(hp, data_points)
            yield indices, hp, constrained_points


class PointConstraint(Constraint):
    """Superclass of constraints acting on sample points.

    The point argument in constrain_points is a HyperPoint.
    """
    __metaclass__ = ABCMeta
    pass


class CellConstraint(Constraint):
    """Superclass of constraints acting on cells surrounding sample points.

    The point argument in constrain_points is a HyperPoint in which the
    coordinate values are of type iris.coords.Cell.
    """
    __metaclass__ = ABCMeta

    def get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data):
        from cis.collocation.col_implementations import HyperPoint
        if missing_data_for_missing_sample:
            iterator = index_iterator_for_non_masked_data(shape, points)
        else:
            iterator = index_iterator_nditer(shape, output_data[0])

        for indices in iterator:
            hp_values = [None] * HyperPoint.number_standard_names
            hp_cell_values = [None] * HyperPoint.number_standard_names
            for (hpi, ci, shi) in coord_map:
                hp_values[hpi] = coords[ci].points[indices[shi]]
                hp_cell_values[hpi] = coords[ci].cell(indices[shi])

            hp = HyperPoint(*hp_values)
            constrained_points = self.constrain_points(HyperPoint(*hp_cell_values), data_points)
            yield indices, hp, constrained_points


# noinspection PyAbstractClass
class IndexedConstraint(Constraint):
    """Superclass of constraints that expect points to be referenced by index.
    """
    __metaclass__ = ABCMeta

    def get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data):
        from cis.collocation.col_implementations import HyperPoint
        if missing_data_for_missing_sample:
            iterator = index_iterator_for_non_masked_data(shape, points)
        else:
            iterator = index_iterator_nditer(shape, output_data[0])

        for indices in iterator:
            hp_values = [None] * HyperPoint.number_standard_names
            for (hpi, ci, shi) in coord_map:
                hp_values[hpi] = coords[ci].points[indices[shi]]

            hp = HyperPoint(*hp_values)
            constrained_points = self.constrain_points(indices, data_points)
            yield indices, hp, constrained_points


def __get_class(parent_class, name=None):
    """
    Identify the subclass of parent_class to a given name, if specified.
    If the name is not specified, the routine picks a default.

    Note, only the first filename of the list is use here.

    :param parent_class: A base class
    :param name: name of the class to find
    :return: a subclass of the parent_class
    """
    from cis.plugin import find_plugin_classes
    from cis.exceptions import ClassNotFoundError
    import logging

    all_classes = find_plugin_classes(parent_class, 'cis.collocation.col_implementations')
    for cls in all_classes:

        if name is None:
            # Use default
            pass
        else:
            # Method specified directly
            if name == cls.__name__:
                logging.debug("Selected class " + cls.__name__)
                return cls

    raise ClassNotFoundError("Specified "+parent_class.__name__+" subclass cannot be found")


def get_kernel(method=None):
    """
    Top level routine for finding the correct Kernel object.
    :param str method: The kernel method to find - this should be a string which matches the name of one
    of the subclasses of Kernel
    :return: One of Kernel's subclasses
    """
    from cis.exceptions import ClassNotFoundError
    try:
        kernel_cls = __get_class(Kernel, method)
    except ClassNotFoundError:
        raise ValueError("No kernel found matching name: " + str(method))
    return kernel_cls
