'''
Module to test the one-dimensional plotting of NetCDF files
These tests have to be run manually
'''
from jasmin_cis.plot import Plotter
from nose.tools import nottest
from jasmin_cis.test.test_files.data import *
import iris
import os.path

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

@nottest # Jenkins can't plot to file or screen
def can_plot_line_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_1d_filename)
    Plotter([cube], "line", out_filename)
    assert(os.path.isfile(out_filename)) 

@nottest # Jenkins can't plot to file or screen
def can_plot_line_graph_to_screen():    
    cube = make_cube(valid_1d_filename)
    Plotter([cube], "line")

@nottest # Jenkins can't plot to file or screen    
def can_plot_scatter_graph_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "scatter", out_filename)
    assert(os.path.isfile(out_filename))

@nottest # Jenkins can't plot to file or screen
def can_plot_scatter_graph_to_screen():    
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "scatter")

@nottest # Jenkins can't plot to file or screen
def can_plot_heatmap_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "heatmap", out_filename)
    assert(os.path.isfile(out_filename))

@nottest # Jenkins can't plot to file or screen
def can_plot_heatmap_to_screen():    
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "heatmap")
    
@nottest # Jenkins can't plot to file or screen
def can_plot_contour_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "contour", out_filename)
    assert(os.path.isfile(out_filename))
   
@nottest # Jenkins can't plot to file or screen
def can_plot_contour_to_screen():    
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "contour")

@nottest # Jenkins can't plot to file or screen
def can_plot_contourf_to_file():    
    delete_file_if_exists()
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "contourf", out_filename)
    assert(os.path.isfile(out_filename))
   
@nottest # Jenkins can't plot to file or screen
def can_plot_contourf_to_screen():    
    cube = make_cube(valid_2d_filename)
    Plotter([cube], "contourf")

if __name__ == "__main__":
    can_plot_line_graph_to_screen()
    #can_plot_scatter_graph_to_screen()
    can_plot_heatmap_to_screen()
    can_plot_contour_to_screen()
    can_plot_contourf_to_screen()
    
    can_plot_line_graph_to_file()
    #can_plot_scatter_graph_to_file()
    can_plot_heatmap_to_file()
    can_plot_contour_to_file()
    can_plot_contourf_to_file()
    print "Finished"