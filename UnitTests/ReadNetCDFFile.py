# Module to test the reading of NetCDF files
from nose.tools import *
import iris

@istest
def x_equals_0():
    x = 0
    eq_(x, 0)
    
@istest
def test_that_fails():
    x = 0
    eq_(x, 1)
    
@istest
def can_read_netcdf_file():       
    filename = "/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    file = iris.load(filename)    
        
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():   
    filename = "invalidfilename"
    file = iris.load(filename)  

@istest
@raises(ValueError)
def should_raise_value_error_with_file_that_is_not_netcdf():      
    filename = "/home/daniel/Desktop/Connect to Jasmin"
    file = iris.load(filename)

@istest
def can_read_15GB_file():
    pass

@istest
@raises(IOError)
def should_raise_io_error_with_file_that_does_not_have_read_permissions():
    filename = "/home/daniel/NetCDF Files/Unreadable Folder/xglnwa.pm.k8dec-k9nov.vprof.tm.nc"
    file = iris.load(filename)    


