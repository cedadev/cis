# InvalidPlotTypeError.py
# Created by PARD on 16th Jan 2013
# Copyright TODO
#
# Error raised when an invalid plot type is entered
class InvalidPlotTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)