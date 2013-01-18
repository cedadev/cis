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
