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