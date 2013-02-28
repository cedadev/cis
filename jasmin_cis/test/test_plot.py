'''
Module to test the one-dimensional plotting of NetCDF files
More tests can be found in the manual_integration_tests package
'''
import os.path

from nose.tools import istest, raises
from jasmin_cis.test.test_files.data import *
import iris
import os.path

from jasmin_cis.plotting.plot import Plotter


def delete_file_if_exists():
    '''
    Used to delete the file that will be created before tests are run
    in order to be able to check after the test if the file was created by the test
    '''
    if os.path.isfile(out_filename):
        os.remove(out_filename)

def make_cube(filename, variable = None):
    if variable is None:
        variable = valid_variable_in_valid_filename
    variable = iris.AttributeConstraint(name = variable)
    cube = iris.load_cube(filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    return cube       
    
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():     
    cube = make_cube("/")
    Plotter([cube], "line", "/")
