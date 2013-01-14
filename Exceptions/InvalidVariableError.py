# InvalidVariableError.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Error raised when an invalid variable is entered
class InvalidVariableError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)