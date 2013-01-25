'''
Module to test the one-dimensional plotting of NetCDF files
'''
from jasmin_cis.plot import plot
from nose.tools import istest, raises
from test_files.data import *
import iris
import os.path
from jasmin_cis.exceptions import *

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
def can_plot_line_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_1d_filename)
    plot([cube], "line", out_filename)   
    assert(os.path.isfile(out_filename))

# Not an automated test   
def can_plot_line_graph_to_screen():    
    cube = make_cube(valid_1d_filename)       
    plot([cube], "line")
    
@istest
def can_plot_scatter_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    plot([cube], "scatter", out_filename)     
    assert(os.path.isfile(out_filename))
    
# Not an automated test    
def can_plot_scatter_graph_to_screen():    
    cube = make_cube(valid_2d_filename)       
    plot([cube], "scatter")

@istest
def can_plot_heatmap_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    plot([cube], "heatmap", out_filename)   
    assert(os.path.isfile(out_filename))
   
# Not an automated test   
def can_plot_heatmap_to_screen():    
    cube = make_cube(valid_2d_filename)       
    plot([cube], "heatmap")
    
@istest
def can_plot_contour_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    plot([cube], "contour", out_filename)   
    assert(os.path.isfile(out_filename))
   
# Not an automated test   
def can_plot_contour_to_screen():    
    cube = make_cube(valid_2d_filename)       
    plot([cube], "contour")

@istest
def can_plot_contourf_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    plot([cube], "contourf", out_filename)   
    assert(os.path.isfile(out_filename))
   
# Not an automated test   
def can_plot_contourf_to_screen():    
    cube = make_cube(valid_2d_filename)       
    plot([cube], "contourf")

    
@istest
@raises(IOError)
def should_raise_io_error_with_invalid_filename():     
    cube = make_cube("/")
    plot([cube], "line", "/")
   
@istest
@raises(InvalidPlotTypeError)
def should_raise_error_when_variable_is_not_1D():
    delete_file_if_exists()
    cube = make_cube(valid_1d_filename, not1Dvariable)
    plot([cube], "line", out_filename)   
    assert(os.path.isfile(out_filename))
    
    
if __name__ == "__main__":
    # Call the methods to plot to screen instead of the plot to file ones
    can_plot_line_graph_to_screen()
    can_plot_scatter_graph_to_screen()
    can_plot_heatmap_to_screen()
    can_plot_contour_to_screen()
    can_plot_contourf_to_screen()