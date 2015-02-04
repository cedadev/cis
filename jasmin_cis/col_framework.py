from abc import ABCMeta, abstractmethod

import numpy as np
from utils import index_iterator_for_non_masked_data, index_iterator_nditer


class Colocator(object):
    '''
    Class which provides a method for performing colocation. This just defines the interface which
    the subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    def __init__(self):
        self.fill_value = np.Infinity

    @abstractmethod
    def colocate(self, points, data, constraint, kernel):
        '''

        :param points: A set of points onto which we will colocate some other 'data'
        :param data: Some other data to be colocated onto the 'points'
        :param constraint: A Constraint instance which provides a fill_value and constrain method
        :param kernel: A Kernel instance which provides a kernel method
        :return: One or more LazyData objects whose coordinates lie on the points defined above

        '''


class Kernel(object):
    '''
    Class which provides a method for taking a number of points and returning one value. For example a nearest
    neighbour algorithm or sort algorithm or mean. This just defines the interface which the subclasses must implement.
    '''
    __metaclass__ = ABCMeta
    return_size = 1

    @abstractmethod
    def get_value(self, point, data):
        """
        :param point: A single HyperPoint
        :param data: A set of data points to reduce to a single value
        :return: For return_size=1 a single value (number) otherwise a list of reutrns values, which represents some
            operation on the points provided

        """

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        """Returns details of extra variables to be created for outputs of kernel.
        :param var_name: base variable name
        :param var_long_name: base variable long name
        :param var_standard_name: base variable standard_name
        :param var_units: base variable units
        :return: tuple of tuples each containing (variable name, variable long name, variable units)
        """
        return ((var_name, var_long_name, var_standard_name, var_units),)


class AbstractDataOnlyKernel(Kernel):
    """
    A Kernel that can work on data only, e.g. mean nly requires the data value to calculate the mean
    """

    __metaclass__ = ABCMeta

    def get_value(self, point, data):
        """
        :param point: A single HyperPoint
        :param data: A set of data points to reduce to a single value
        :return: For return_size=1 a single value (number) otherwise a list of reutrns values, which represents some
            operation on the points provided

        """
        values = data.vals
        if len(values) == 0:
            raise ValueError
        return self.get_value_for_data_only(values)

    @abstractmethod
    def get_value_for_data_only(self, values):
        """
        Return a value or values base on the data
        :param values: a numpy array of values (can not be none or empty)
        :return: single data item if return_size is 1 or a list of items containing return size items
        :throws ValueError: if there are any problems creating a value
        """


class Constraint(object):
    '''
    Class which provides a method for constraining a set of points. A single HyperPoint is given as a reference
    but the data points to be reduced ultimately may be of any type. This just defines the interface which the
    subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def constrain_points(self, point, data):
        '''

        :param point: A single HyperPoint
        :param data: A set of data points to be reduced
        :return: A reduced set of data points

        '''

    def get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data):
        """
        Iterator to iterate through the points needed to be calculated
        The default iterator, iterates through all the sample points calling constrain_points for each one
        :param missing_data_for_missing_sample: if true anywhere there is missing data on the sample then final point is
            missing; otherwise just use the sample
        :param coord_map: coordinate map - list of tuples of indexes of hyperpoint coord, data coords and output coords
        :param coords: the coordinates to map to
        :param data_points: the data points (without masked values)
        :param shape: shape of the final values
        :param points: the original points object, these are the points to colocate
        :param output_data: output data set
        :return: iterator which iterates through sample indices, hyper point and constrained points to be placed in
            these points
        """
        from jasmin_cis.col_implementations import HyperPoint
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
        from jasmin_cis.col_implementations import HyperPoint
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
        from jasmin_cis.col_implementations import HyperPoint
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
    '''
    Identify the subclass of parent_class to a given name, if specified.
    If the name is not specified, the routine picks a default.

    Note, only the first filename of the list is use here.

    :param parent_class: A base class
    :param name: name of the class to find
    :return: a subclass of the parent_class
    '''
    from jasmin_cis.plugin import find_plugin_classes
    from jasmin_cis.exceptions import ClassNotFoundError
    import logging

    all_classes = find_plugin_classes(parent_class, 'jasmin_cis.col_implementations')
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


def get_constraint(method=None):
    '''
    Top level routine for finding the correct Constraint object. This doesn't instantiate the constraint class as it
    may need variables passed to the constructor

    :param method: The constraint method to find - this should be a string which matches the name of one
    of the subclasses of Constraint
    :return: One of Constraint's subclasses
    '''
    constraint_cls = __get_class(Constraint, method)
    return constraint_cls


def get_kernel(method=None):
    '''
    Top level routine for finding the correct Kernel object.

    :param method: The kernel method to find - this should be a string which matches the name of one
    of the subclasses of Kernel
    :return: One of Kernel's subclasses
    '''
    kernel_cls = __get_class(Kernel, method)
    return kernel_cls


def get_colocator(method=None):
    '''
    Top level routine for finding the correct Colocator object.

    :param method: The colocate method to find - this should be a string which matches the name of one
    of the subclasses of Colocator
    :return: One of Colocator's subclasses
    '''
    colocate_cls = __get_class(Colocator, method)
    return colocate_cls
