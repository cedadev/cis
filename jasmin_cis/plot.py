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

class plot_type(object):
    def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
        self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        
plot_types = {'line' : plot_type(None, 1, plot_line),
                #'scatter' : plot_type(MAXIMUM_NUMBER_OF_VARIABLES, 2, qplt.points), 
                'heatmap' : plot_type(1, 2, plot_heatmap),
                'contour' : plot_type(1, 2, plot_contour),
                'contourf' : plot_type(1, 2, plot_contourf)}

default_plot_types = { 1 : 'line',
                       2 : 'heatmap'}

def format_plot(data, options, plot_type, datafiles): 
    '''
    Sets the fontsize, xlabel, ylabel, title, legend and coastlines where appropriate.
    Tries to assign default value if value not specified
    '''   
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

def set_width_and_height(kwargs):
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

def plot(data, plot_type = None, out_filename = None, *args, **kwargs):
    '''
    Note: Data must be a list
    This method needs commenting
    '''
    import jasmin_cis.exceptions as ex
    import logging
    
    kwargs = set_width_and_height(kwargs)    
    
    variable_dim = len(data[0].shape)
    
    for key in kwargs.keys():
        if kwargs[key] is None:
            kwargs.pop(key)
    
    options = {}
    for key in plot_options.keys():
        options[key] = kwargs.pop(key, None)
            
    num_variables = len(data)
    
    for item in data:
        if len(item.shape) != variable_dim:
            raise ex.InconsistentDimensionsError("Number of dimensions must be consistent across variables")
        
    if plot_type is None:
        try:
            plot_type = default_plot_types[variable_dim]
        except KeyError:
            raise ex.InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")
    elif plot_types[plot_type].variable_dimensions != variable_dim:
        raise ex.InvalidPlotTypeError("The plot type is not valid for this variable, the dimensions do not match")
    
    if plot_type != "line":
        # Remove color if specified for plot where type is not line    
        arg = kwargs.pop("color", None)        
        if arg is not None:
            logging.warn("Cannot specify a line colour for plot type '" + plot_type + "', did you mean to use cmap?")
    else:
        arg = kwargs.pop("cmap", None)
        if arg is not None:
            logging.warn("Cannot specify a colour map for plot type '" + plot_type + "', did you mean to use color?")
    

    if plot_types[plot_type].maximum_no_of_expected_variables is not None:
        if num_variables > plot_types[plot_type].maximum_no_of_expected_variables:
            raise ex.InvalidPlotTypeError("The plot type is not valid for this number of variables")
    # else: There are an unlimited number of variables for this plot type
    
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
    
    if plot_type == "line" and valrange is not None:
        plt.ylim(**valrange)
        
    if options is not None:
        format_plot(data, options, plot_type, datafiles)
 
    if out_filename is None:
        plt.show()  
    else:
        plt.savefig(out_filename) # Will overwrite if file already exists        