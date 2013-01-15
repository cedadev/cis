# Plot1DNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the one-dimensional plotting of NetCDF files
from Plotting.Plotter import Plotter
from Exceptions.InvalidDimensionError import InvalidDimensionError
from Exceptions.InvalidVariableError import InvalidVariableError
from nose.tools import istest, with_setup, raises
from UnitTests.Strings import valid_filename, valid_variable, invalid_variable, not1Dvariable

myplotter = Plotter()

def setup():
    myplotter = Plotter()

@istest
@with_setup(setup)
def can_plot_specified_variable_in_netcdf_file():
    filename = valid_filename
    variable = valid_variable    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidVariableError)
@with_setup(setup)
def should_raise_error_when_variable_does_not_exist_in_file():
    filename = valid_filename
    variable = invalid_variable    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidDimensionError)
@with_setup(setup)
def should_raise_error_when_variable_is_not_1D():
    filename = valid_filename
    variable = not1Dvariable   
    myplotter.plot1D(filename, variable)
    
