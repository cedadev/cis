from abc import ABCMeta, abstractmethod


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
