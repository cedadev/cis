from abc import ABCMeta, abstractmethod


class SubsetterInterface(object):
    """Interface for subsetter classes.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def subset(self, data, constraint):
        """Subsets the supplied data using the supplied constraint.

        :param data: data to be subsetted
        :param constraint: SubsetConstraint object to be used to subset data
        :return: subsetted data
        """


class SubsetConstraintInterface(object):
    """Interface for subset constraint classes.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
