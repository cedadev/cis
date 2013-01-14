# InvalidDimensionError.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Error raised when an invalid dimension is entered
class InvalidDimensionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)