# Plotter.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Class for plotting graphs
from Exceptions.InvalidDimensionError import InvalidDimensionError
from Exceptions.InvalidVariableError import InvalidVariableError

class Plotter():
    variables = [["nameofvariable", "not1Dvariable"], [1, 2]]
    
    def plot1D(self, filename, variable):
        if (variable not in self.variables[0][:]):
            raise InvalidVariableError(variable + " cannot be found")
        else:
            indexOfVariable = self.variables[0][:].index(variable)
            dimensionsOfVariable = self.variables[1][indexOfVariable]
            
            if (dimensionsOfVariable != 1):
                raise InvalidDimensionError(variable + " does not have one dimension")
        