# NoVariablesSpecifiedError.py
# Created by WALDM on 15th Jan 2013
# Copyright TODO
#
# Error raised when no variables are entered
class NoVariablesSpecifiedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)