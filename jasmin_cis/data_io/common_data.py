from abc import ABCMeta, abstractmethod


class CommonData(object):
    """
    Interface of common methods implemented for gridded and ungridded data.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_coordinates_points(self):
        pass

    @abstractmethod
    def get_all_points(self):
        pass

    @abstractmethod
    def get_non_masked_points(self):
        pass
