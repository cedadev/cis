# InvalidChartTypeError.py
# Created by WALDM on 15th Jan 2013
# Copyright TODO
#
# Error raised when an invalid chart type is entered
class InvalidChartTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)