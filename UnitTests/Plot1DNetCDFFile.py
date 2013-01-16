# Plot1DNetCDFFile.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the one-dimensional plotting of NetCDF files
from Plotting import Plotter
from nose.tools import istest, raises
from UnitTests.StringsUsedInTests import valid_1d_filename, valid_2d_filename, valid_variable_in_valid_filename, out_filename
import iris
import os.path

def delete_file_if_exists():
    if os.path.isfile(out_filename):
        os.remove(out_filename)

def make_cube(filename):
    variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    return cube       

@istest
def can_plot_line_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_1d_filename)
    Plotter.plot_line_graph(cube, out_filename)   
    assert(os.path.isfile(out_filename))

# Not an automated test   
def can_plot_line_graph_to_screen():    
    cube = make_cube(valid_1d_filename)       
    Plotter.plot_line_graph(cube)
    
@istest
def can_plot_scatter_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    Plotter.plot_scatter_graph(cube, out_filename)   
    assert(os.path.isfile(out_filename))
    
# Not an automated test   
def can_plot_scatter_graph_to_screen():    
    cube = make_cube(valid_2d_filename)       
    Plotter.plot_scatter_graph(cube)
    
# Not an automated test   
def can_plot_heatmap_to_screen():    
    cube = make_cube(valid_2d_filename)       
    Plotter.plot_heatmap(cube)
    
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():     
    cube = make_cube(valid_1d_filename)
    Plotter.plot_line_graph(cube, "/")
    
if __name__ == "__main__":
    can_plot_line_graph_to_screen()
    can_plot_scatter_graph_to_screen()
    can_plot_heatmap_to_screen()