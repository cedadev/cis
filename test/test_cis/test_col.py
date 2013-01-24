'''
 Module to test the colocation routines
'''
import jasmin_cis.col as col
from nose.tools import istest, raises
from test_cis.data import *
import iris
import os.path
from jasmin_cis.exceptions import *

#def make_cube(filename, variable = None):
#    if variable is None:
#        variable = valid_variable_in_valid_filename
#    variable = iris.AttributeConstraint(name = variable)
#    cube = iris.load_cube(filename, variable) 
#    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
#    return cube

def make_1d_ungridded_data():
    pass

def make_2d_ungridded_data():
    pass

def make_1d_cube():
    pass

def make_2d_cube():
    pass

@istest
def can_col_gridded_to_ungridded_using_nn_in_1d():
    cube = make_1d_cube()
    ungridded = make_1d_ungridded_data()
    col_data = col.col(cube, ungridded,'nn')
    assert(col.is_colocated(col_data, cube))
