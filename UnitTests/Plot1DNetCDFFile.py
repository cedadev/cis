# Plot1DNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the one-dimensional plotting of NetCDF files
from Plotting import Plotter
from nose.tools import istest
from UnitTests.StringsUsedInTests import valid_filename, valid_variable_in_valid_filename
import iris

@istest
def can_plot_cube():    
    variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(valid_filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]   
    Plotter.plot1D(cube)


    
