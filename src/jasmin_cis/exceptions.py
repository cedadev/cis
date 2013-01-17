# Created by PARD on 16th Jan 2013
# Copyright TODO
#
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
