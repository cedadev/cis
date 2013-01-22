'''
Module to test the plot formatting options
'''
from jasmin_cis.plot import plot
from nose.tools import istest
import iris
from data import *

def make_cube(filename, variable = None):
    if variable is None:
        variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    return cube 

@istest
def can_set_line_colour_to_valid_colour():   
    cube = make_cube(valid_1d_filename)
    plot([cube], "line", out_filename, **{"color" : "green"})  
    