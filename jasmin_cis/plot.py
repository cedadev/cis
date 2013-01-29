'''
Module for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import matplotlib.pyplot as plt
from data_io.read_gridded import unpack_cube

plot_options = { 'title' : plt.title,
              'xlabel' : plt.xlabel, 
              'ylabel' : plt.ylabel,
              'fontsize' : plt.rcParams.update } 

def plot_line(data, *args, **kwargs):
    plt.plot(data["x"], data["data"], *args, **kwargs )

def plot_heatmap(data, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    basemap = Basemap()    
    basemap.pcolormesh(data["x"], data["y"], data["data"], latlon = True, *args, **kwargs)
    basemap.drawcoastlines()   
    
def plot_contour(data, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    basemap = Basemap()    
    basemap.contour(data["x"], data["y"], data["data"], latlon = True, *args, **kwargs)
    basemap.drawcoastlines()    
    
def plot_contourf(data, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    basemap = Basemap()    
    basemap.contourf(data["x"], data["y"], data["data"], latlon = True, *args, **kwargs)
    basemap.drawcoastlines()  

def plot_scatter(data, *args, **kwargs):
    from math import pow
    plt.scatter(data["x"], data["y"], s = pow(kwargs.pop("pointsize", 20), 2), c=data["data"])

class PlotType(object):
    def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
        self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        
plot_types = {'line' : PlotType(None, 1, plot_line),
                'scatter' : PlotType(None, 2, plot_scatter), 
                'heatmap' : PlotType(1, 2, plot_heatmap),
                'contour' : PlotType(1, 2, plot_contour),
                'contourf' : PlotType(1, 2, plot_contourf)}

default_plot_types = { 1 : 'line',
                       2 : 'heatmap'}

def __format_plot(data, options, plot_type, datafiles): 
    '''
    Sets the fontsize, xlabel, ylabel, title, legend and coastlines where appropriate.
    Tries to assign default value if value not specified
    '''
    if options is not None:   
        if options["fontsize"] is not None:
            options["fontsize"] = { "font.size" : float(options["fontsize"]) }   
        else:
            options.pop("fontsize")      
        
        # If any of the options have not been specified, then use the defaults
        if plot_type == "line":
            if options["xlabel"] is None:
                for dim in xrange(len(data[0].shape)):
                    for coord in data[0].coords(contains_dimension=dim, dim_coords=True):
                        xlabel = coord.name()
                options["xlabel"] = xlabel.capitalize()
            if options["ylabel"] is None:
                if len(data) == 1:
                    options["ylabel"] = data[0].long_name.title()
                else:
                    options["ylabel"] = str(data[0].units)
        else:
            options["xlabel"] = ""
            options["ylabel"] = ""
        
        legend_titles = []
        for i, item in enumerate(data):
            if datafiles is not None and datafiles[i]["label"]:
                legend_titles.append(datafiles[i]["label"])
            else:
                legend_titles.append(" ".join(item.long_name.title().split()[:-1]))
            
        if not options["title"]:
            options["title"] = ""
            
        if plot_type != "line":
            if not options["title"]:
                options["title"] = data[0].long_name.title()            
        
        for option, value in options.iteritems():        
            plot_options[option](value)       
        
        if plot_type == "line":
            plt.legend(legend_titles, loc="best")

def __set_width_and_height(kwargs):
    '''
    Sets the width and height of the plot
    Uses an aspect ratio of 4:3 if only one of width and height are specified
    '''
    height = kwargs.pop("height", None)
    width = kwargs.pop("width", None)
    
    if height is not None:
        if width is None:            
            width = height * (4.0 / 3.0)
    elif width is not None:
        height = width * (3.0 / 4.0)
        
    if height is not None and width is not None:
        plt.figure(figsize = (width, height))
        
    return kwargs

def __do_plot(data, plot_type, args, kwargs):
    datafiles = kwargs.pop("datafiles", None) 
    for i, item in enumerate(data):
        # Temporarily add args to kwargs
        if plot_type == "line" and datafiles is not None:
            if datafiles[i]["linestyle"]:
                kwargs["linestyle"] = datafiles[i]["linestyle"]
            if datafiles[i]["color"]:
                kwargs["color"] = datafiles[i]["color"]
        item_to_plot = unpack_cube(item)
        plot_types[plot_type].plot_method(item_to_plot, *args, **kwargs)
        # Remove temp args
        if plot_type == "line" and datafiles is not None:
            if datafiles[i]["linestyle"]:
                kwargs.pop("linestyle")
            if datafiles[i]["color"]:
                kwargs.pop("color")
    return datafiles

def __warn_if_incorrect_colour_type_used(plot_type, kwargs):
    import logging
    if plot_type != "line": # Remove color if specified for plot where type is not line
        arg = kwargs.pop("color", None)
        if arg is not None:
            logging.warn("Cannot specify a line colour for plot type '" + plot_type + "', did you mean to use cmap?")
    else:
        arg = kwargs.pop("cmap", None)
        if arg is not None:
            logging.warn("Cannot specify a colour map for plot type '" + plot_type + "', did you mean to use color?")

def __set_default_plot_type(variable_dim):
    from jasmin_cis.exceptions import InvalidPlotTypeError
    try:
        plot_type = default_plot_types[variable_dim]
    except KeyError:
        raise InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")
    return plot_type

def __check_plot_type_is_valid_for_given_variable(plot_type, variable_dim):
    from jasmin_cis.exceptions import InvalidPlotTypeError
    if plot_types[plot_type].variable_dimensions != variable_dim:
        raise InvalidPlotTypeError("The plot type is not valid for this variable, the dimensions do not match")

def __check_all_data_items_are_of_same_shape(data, variable_dim):
    from jasmin_cis.exceptions import InconsistentDimensionsError
    for item in data:
        if len(item.shape) != variable_dim:
            raise InconsistentDimensionsError("Number of dimensions must be consistent across variables")

def __check_number_of_variables_does_not_exceed_maximum(plot_type, num_variables):
    from jasmin_cis.exceptions import InvalidPlotTypeError
    if plot_types[plot_type].maximum_no_of_expected_variables is not None:
        if num_variables > plot_types[plot_type].maximum_no_of_expected_variables:
            raise InvalidPlotTypeError("The plot type is not valid for this number of variables") # else: There are an unlimited number of variables for this plot type

def __prepare_val_range(plot_type, **kwargs):
    valrange = kwargs.pop("valrange", None)
    
    if plot_type != "line" and valrange is not None:
        try:
            kwargs["vmin"] = valrange.pop("ymin")
        except KeyError:
            pass
        
        try:
            kwargs["vmax"] = valrange.pop("ymax")
        except KeyError:
            pass
        
    return valrange, kwargs

def __output_to_file_or_screen(out_filename):
    if out_filename is None:
        plt.show()
    else:
        plt.savefig(out_filename) # Will overwrite if file already exists

def __remove_unassigned_arguments(kwargs):
    for key in kwargs.keys():
        if kwargs[key] is None:
            kwargs.pop(key)

def __create_plot_format_options(kwargs):
    options = {}
    for key in plot_options.keys():
        options[key] = kwargs.pop(key, None)
    
    return options

def __apply_line_graph_value_limits(plot_type, valrange):
    if plot_type == "line" and valrange is not None:
        plt.ylim(**valrange)

def __validate_data(data, plot_type, kwargs, variable_dim):
    __check_all_data_items_are_of_same_shape(data, variable_dim)
    __check_plot_type_is_valid_for_given_variable(plot_type, variable_dim)
    __warn_if_incorrect_colour_type_used(plot_type, kwargs)
    __check_number_of_variables_does_not_exceed_maximum(plot_type, len(data))

def plot(data, plot_type = None, out_filename = None, *args, **kwargs):
    '''
    The main plotting method
    
    args:
        data:         A list of data objects (cubes or ungridded data objects)
        plot_type:    The type of the plot to be plotted. A default will be chosen if omitted
        out_filename: The filename of the file to save the plot to
    '''
             
    __remove_unassigned_arguments(kwargs)   
       
    variable_dim = len(data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
    
    if plot_type is None:
        plot_type = __set_default_plot_type(variable_dim)
    
    __validate_data(data, plot_type, kwargs, variable_dim)
    
    plot_format_options = __create_plot_format_options(kwargs)
    valrange, kwargs = __prepare_val_range(plot_type, **kwargs)  
    kwargs = __set_width_and_height(kwargs)  
       
    datafiles = __do_plot(data, plot_type, args, kwargs)  
    __apply_line_graph_value_limits(plot_type, valrange)
        
    __format_plot(data, plot_format_options, plot_type, datafiles) 
    
    __output_to_file_or_screen(out_filename)        