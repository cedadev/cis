# Plot1DNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the one-dimensional plotting of NetCDF files
from Plotting import Plotter
from nose.tools import istest, raises
from UnitTests.StringsUsedInTests import valid_filename, valid_variable_in_valid_filename, out_filename
import iris
import os.path

@istest
def can_plot_cube_to_file():    
    if os.path.isfile(out_filename):
        os.remove(out_filename)
    
    variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(valid_filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]   
    Plotter.plotLineGraph(cube, out_filename)
    
    assert(os.path.isfile(out_filename))
    
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():    
    variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(valid_filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]   
    Plotter.plotLineGraph(cube, "/")

    
