'''
 Module to test the colocation routines
'''
from jasmin_cis.col import Colocator
from nose.tools import istest, raises, nottest
from test_files.data import *
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

def is_colocated(data1, data2):
    '''
        Checks wether two datasets share all of the same points, this might be useful
        to determine if colocation is necesary or completed succesfully
    '''
    colocated = len(data1) == len(data2)
    if colocated:
        for point1 in data1:
            colocated = all( point1 == point2 for point2 in data2 )
            if not colocated:
                return colocated
    return colocated

#Duncan to fix
@nottest
def can_col_gridded_to_ungridded_using_nn_in_1d():
    cube = make_1d_cube()
    ungridded = make_1d_ungridded_data()
    col = Colocator(cube, ungridded,'nn')
    col.colocate()
    assert(is_colocated(col.data, cube))