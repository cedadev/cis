from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class SubsetConstraintInterface(object):
    """Interface for subset constraint classes.
    """

    @abstractmethod
    def constrain(self, data):
        """Subsets the supplied data.

        :param data: data to be subsetted
        :return: subsetted data
        """
