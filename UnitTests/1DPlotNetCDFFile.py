# 1DPlotNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the one-dimensional plotting of NetCDF files
from Exceptions import InvalidVariableError, InvalidDimensionError
from Plotting.Plotter import *
from nose.tools import *

myplotter = Plotter()

def setup():
    myplotter = Plotter()

@istest
@with_setup(setup)
def can_plot_specified_variable_in_netcdf_file():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "nameofvariable"    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidVariableError)
@with_setup(setup)
def should_raise_error_when_variable_does_not_exist_in_file():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "invalidvariable"    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidDimensionError)
@with_setup(setup)
def should_raise_error_when_variable_is_not_1D():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "not1Dvariable"    
    myplotter.plot1D(filename, variable)
    
