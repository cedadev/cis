# 1DPlotNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the reading of NetCDF files
from nose.tools import *
import iris

@istest
def can_plot_specified_variable_in_netcdf_file():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "nameofvariable"
    myplotter.plot1D(filename, variable, toscreen)
    
@istest
@raises(InvalidVariableError)
def should_raise_error_when_variable_does_not_exist_in_file():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "invalidvariable"
    myplotter.plot1D(filename, variable, toscreen)
    
@istest
@raises(InvalidDimensioneError)
def should_raise_error_when_variable_is_not_1D():
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    variable = "invalidvariable"
    myplotter.plot1D(filename, variable, toscreen)
    
