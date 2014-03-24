from abc import ABCMeta, abstractmethod


class CommonData(object):
    """
    Interface of common methods implemented for gridded and ungridded data.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_coordinates_points(self):
        """Returns a list-like object allowing access to the coordinates of all points as HyperPoints.
        The object should allow iteration over points and access to individual points.
        @return: list-like object of data points
        """
        pass

    @abstractmethod
    def get_all_points(self):
        """Returns a list-like object allowing access to all points as HyperPoints.
        The object should allow iteration over points and access to individual points.
        @return: list-like object of data points
        """
        pass

    @abstractmethod
    def get_non_masked_points(self):
        """Returns a list-like object allowing access to all points as HyperPoints.
        The object should allow iteration over non-masked points and access to individual points.
        @return: list-like object of data points
        """
        pass
