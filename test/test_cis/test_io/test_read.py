# ReadNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the reading of NetCDF files
from nose.tools import istest, raises
import iris
from test_cis.data import *
    
@istest
def can_read_netcdf_file():       
    filename = valid_1d_filename
    iris.load(filename)    
        
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():   
    filename = invalid_filename
    iris.load(filename)  

@istest
@raises(ValueError)
def should_raise_value_error_with_file_that_is_not_netcdf():      
    filename = non_netcdf_file
    iris.load(filename)

@istest
def can_read_15GB_file():
    pass

@istest
@raises(IOError)
def should_raise_io_error_with_file_that_does_not_have_read_permissions():
    filename = file_without_read_permissions
    iris.load(filename)    

@istest
def can_read_netcdf_file_with_incorrect_file_extension():
    filename = netcdf_file_with_incorrect_file_extension
    iris.load(filename)  

@istest
@raises(ValueError)
def should_raise_value_error_with_file_that_has_netcdf_extension_but_is_not_netcdf():
    filename = non_netcdf_file_with_netcdf_file_extension
    iris.load(filename) 

@istest
def can_get_number_of_variables_in_file():
    #filename = valid_filename
    #netcdf_file = iris.load(filename)   
    #eq_(Controller.get_number_of_variables(netcdf_file), 466)
    # TODO
    pass

'''    
@istest
def can_plot_specified_variable_in_netcdf_file():
    filename = valid_filename
    variable = valid_variable    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidVariableError)
def should_raise_error_when_variable_does_not_exist_in_file():
    filename = valid_filename
    variable = invalid_variable    
    myplotter.plot1D(filename, variable)
    
@istest
@raises(InvalidDimensionError)
def should_raise_error_when_variable_is_not_1D():
    filename = valid_filename
    variable = not1Dvariable   
    myplotter.plot1D(filename, variable)
    '''