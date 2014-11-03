from abc import abstractmethod, ABCMeta


class Indexable(object):
    """
    Represents an object which can be indexed using Elasticsearch
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def type(self):
        """
        Returns the objects Elasticsearch type
        """

    @abstractmethod
    def body(self):
        """
        Converts this object to a JSON representation
        """


class FileMetadata(Indexable):
    """
    This class represents the metadata
    """

    path = ''
    filename = ''
    size = 0


    def body(self):
        pass

    def type(self):
        pass
