# Plotter.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Class for plotting graphs

'''from Exceptions.InvalidDimensionError import InvalidDimensionError
from Exceptions.InvalidVariableError import InvalidVariableError
import Controller'''
import iris.plot as iplt
import matplotlib.pyplot as plt

#class Plotter():   
    #def plot1D(self, data, kwargs**):
def plot1D(data):
    iplt.plot(data)    
    plt.show()
    '''if (variable not in Controller.variables[0][:]):
        raise InvalidVariableError("'" + variable + "' cannot be found in '" + filename + "'")
    else:
        indexOfVariable = Controller.variables[0][:].index(variable)
        dimensionsOfVariable = Controller.variables[1][indexOfVariable]
        
        if (dimensionsOfVariable != 1):
            raise InvalidDimensionError("'" + variable + "' does not have one dimension")'''
        