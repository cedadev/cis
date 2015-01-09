from abc import ABCMeta, abstractmethod

import numpy as np


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
    Class which provides a method for taking a number of points and returning one value. This could be a nearest
    neighbour algorithm or some sort of algorithm. This just defines the interface which the subclasses must implement.
    '''
    __metaclass__ = ABCMeta
    return_size = 1

    @abstractmethod
    def get_value(self, point, data):
        '''
        :param point: A single HyperPoint
        :param data: A set of data points to reduce to a single value
        :return: A single value (number) which represents some operation on the points provided

        '''

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        """Returns details of extra variables to be created for outputs of kernel.
        :param var_name: base variable name
        :param var_long_name: base variable long name
        :param var_standard_name: base variable standard_name
        :param var_units: base variable units
        :return: tuple of tuples each containing (variable name, variable long name, variable units)
        """
        return None


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
    pass


class IndexedConstraint(Constraint):
    """Superclass of constraints that expect points to be referenced by index.
    """
    __metaclass__ = ABCMeta
    pass


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
