from abc import ABCMeta, abstractmethod


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
        values = data.values
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
        pass


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
