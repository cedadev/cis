'''
Module to test the plot formatting options
Don't need to test things that would be caught in the parser, e.g. invalid font size
These tests have to be run manually
'''
from nose.tools import raises, nottest
import iris

from plotting.plot import Plotter
from jasmin_cis.test.test_files.data import *


def make_cube(filename, variable = None):
    if variable is None:
        variable = iris.AttributeConstraint(name = valid_variable_in_valid_filename)
    cube = iris.load_cube(filename, variable) 
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    return cube 

@nottest # Jenkins can't plot to file or screen
def can_set_line_colour_to_valid_colour():   
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"color" : valid_colour})
        
@nottest # Jenkins can't plot to file or screen
def should_not_raise_error_if_colour_is_specified_for_invalid_chart_type(): # Simply discard the colour specified 
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, **{"color" : valid_colour})
    
@nottest # Jenkins can't plot to file or screen
def can_set_line_width_to_valid_width():   
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"itemwidth" : valid_width})
    
@nottest # Jenkins can't plot to file or screen
def can_set_line_style_to_valid_style():   
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"linestyle" : valid_line_style})
    
@nottest # Jenkins can't plot to file or screen
def can_set_colour_map_to_valid_colour():   
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, **{"cmap" : valid_colour_map})
    
@nottest # Jenkins can't plot to file or screen
@raises(ValueError)
def should_raise_valueerror_with_invalid_colour_map():   
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, **{"cmap" : invalid_colour_map})

@nottest # Jenkins can't plot to file or screen    
def can_set_font_size_to_valid_size():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"fontsize" : valid_font_size})

@nottest # Jenkins can't plot to file or screen    
def can_set_plot_width_alone():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"width" : valid_width})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_plot_height_alone():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"height" : valid_height})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_plot_width_and_height():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, **{"height" : valid_height, "width" : valid_width})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_ymin_alone():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymin" : valid_ymin})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_ymax_alone():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymax" : valid_ymax})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_ymin_and_ymax():
    cube = make_cube(valid_1d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymin" : valid_ymin, "ymax" : valid_ymax})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_vmin_alone():
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymin" : valid_ymin})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_vmax_alone():
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymax" : valid_ymax})
    
@nottest # Jenkins can't plot to file or screen    
def can_set_vmin_and_vmax():
    cube = make_cube(valid_2d_filename)
    Plotter([cube], out_filename = out_filename, valrange = {"ymin" : valid_ymin, "ymax" : valid_ymax})

if __name__ == "__main__":
    can_set_line_colour_to_valid_colour()
    should_not_raise_error_if_colour_is_specified_for_invalid_chart_type()
    can_set_line_width_to_valid_width()
    can_set_line_style_to_valid_style()
    can_set_colour_map_to_valid_colour()
    should_raise_valueerror_with_invalid_colour_map()
    can_set_font_size_to_valid_size()
    can_set_plot_height_alone()
    can_set_plot_width_alone()
    can_set_plot_width_and_height()
    can_set_ymin_alone()
    can_set_ymax_alone()
    can_set_ymin_and_ymax()
    can_set_vmin_alone()
    can_set_vmax_alone()
    can_set_vmin_and_vmax()
    print "Finished running tests"