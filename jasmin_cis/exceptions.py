"""
Custom CIS exceptions
"""

class CISError(Exception):
    pass

class InvalidPlotTypeError(CISError):
    pass

class InvalidDimensionError(CISError):
    pass

class InvalidVariableError(CISError):
    pass

class InconsistentDimensionsError(CISError):
    pass

class InvalidPlotFormatError(CISError):
    pass

class InvalidFileExtensionError(CISError):
    pass

class InvalidDataTypeError(CISError):
    pass

class InvalidColocationMethodError(CISError):
    pass

class InvalidLineStyleError(CISError):
    pass

class InvalidHistogramStyleError(CISError):
    pass

class CoordinateNotFoundError(CISError):
    pass

class DuplicateCoordinateError(CISError):
    pass

class ClassNotFoundError(CISError):
    pass

class InvalidCommandLineOptionError(CISError):
    pass

class InvalidNumberOfDatagroupsSpecifiedError(CISError):
    pass

class NotEnoughAxesSpecifiedError(CISError):
    pass

class InvalidSliceIndexError(CISError):
    pass

class NoDataInSubsetError(CISError):
    pass


class FileFormatError(CISError):
    """
    Throw when there is an error determining the type of a file
    """
    error_list = ['Unknown error']

    def __init__(self, error_list, *args, **kwargs):
        super(FileFormatError, self).__init__(args, kwargs)
        self.error_list = error_list


class UserPrintableException(CISError):
    """
    This exception is thrown if the program has failed for a known reason. This message is printed without a stack trace
    """
    def __init__(self, message):
        """
        Constructor
        :param message: the message to show the user
        :return: nothing
        """
        super(UserPrintableException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message
