# Plotter.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Class for plotting graphs

import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
from UnitTests.StringsUsedInTests import valid_variable_in_valid_filename, valid_filename
import Parser
   
def plot1D(data, out_filename = None, *args, **kwargs):    
    iplt.plot(data, *args, **kwargs)    
    if out_filename == None:
        plt.show()
    else:
        plt.savefig(out_filename)

args = Parser.parse_args([valid_filename, "-v", valid_variable_in_valid_filename])

variable = iris.AttributeConstraint(name = args.variables[0]) 
cube = iris.load_cube(args.filenames, variable)
cube = list(cube.slices([coord for coord in cube.coords() if coord.points.size > 1]))[0] 

kwargs = {"title" : "My title"}
plot1D(cube, **kwargs)
        