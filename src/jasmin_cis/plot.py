'''
Module for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import iris.quickplot as qplt
import iris.plot as iplt
import matplotlib.pyplot as plt
import iris.coords as crds

plot_options = { #'title' : plt.title,
              'xlabel' : plt.xlabel, 
              'ylabel' : plt.ylabel,
              'fontsize' : plt.rcParams.update } 

class plot_type(object):
    def __init__(self, expected_no_of_variables, variable_dimensions, plot_method, is_map):
        self.expected_no_of_variables = expected_no_of_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        self.is_map = is_map
        

def my_contour(cube, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    
    data = cube.data
    mode = crds.POINT_MODE
    plot_defn = iplt._get_plot_defn(cube, mode, ndims=2)
    
    # Obtain U and V coordinates
    v_coord, u_coord = plot_defn.coords
    if u_coord:
        u = u_coord.points
    else:
        u = np.arange(data.shape[1])
    if v_coord:
        v = v_coord.points
    else:
        v = np.arange(data.shape[0])

    m = Basemap()
    #m = Basemap(projection='robin',lon_0=0.5*(v[0]+v[-1]))

    x, y = m(*np.meshgrid(u,v))

    #print x, np.ptp(x)
    #print y, np.ptp(y)
    #print data

    cs = m.pcolormesh(x,y,data,latlon=True)
    m.drawcoastlines()
    plt.show()

plot_types = {'line' : plot_type(1, 1, qplt.plot, False),
                'scatter' : plot_type(1, 2, qplt.points, False), 
                'heatmap' : plot_type(1, 2, qplt.pcolormesh, True),
                'contour' : plot_type(1, 2, qplt.contour, True),
                'contourf' : plot_type(1, 2, qplt.contourf, True)}

default_plot_types = { 1 : 'line',
                       2 : 'heatmap'}

def format_plot(data, options, plot_type):    
    if options["fontsize"] is not None:
        options["fontsize"] = { "font.size" : float(options["fontsize"]) }   
    else:
        options.pop("fontsize")      
    
    # If any of the options have not been specified, then use the defaults
    if options["xlabel"] is None:
        for dim in xrange(len(data.shape)):
            for coord in data.coords(contains_dimension=dim, dim_coords=True):
                xlabel = coord.name()
        options["xlabel"] = xlabel.capitalize()
    if options["ylabel"] is None:
        options["ylabel"] = data.long_name.title()
    
    for option, value in options.iteritems():        
        plot_options[option](value)       
    
    if plot_types[plot_type].is_map:
        # Try and add the coast lines if the map supports it
        try:
            plt.gca().coastlines()
        except AttributeError:
            pass
 
    plt.legend(loc="upper left")

def set_width_and_height(kwargs):
    height = None
    width = None
    
    if kwargs["height"] is not None:
        height = kwargs.pop("height")
        if kwargs["width"] is not None:            
            width = kwargs.pop("width")
        else:
            width = height * (4.0 / 3.0)
    elif kwargs["width"] is not None:
        width = kwargs.pop("width")
        height = width * (3.0 / 4.0)
        
    if height is not None and width is not None:
        plt.figure(figsize = (width, height))
        
    return kwargs

def plot(data, plot_type = None, out_filename = None, *args, **kwargs):
    '''
    Note: Data must be a list of cubes
    '''
    import jasmin_cis.exceptions as ex
    import logging
    
    kwargs = set_width_and_height(kwargs)    
    
    # Unpack the data list if there is only one element, otherwise the whole list
    # gets passed to the plot function. This could be done with unpacking in the 
    # plot method call but we already unpack the args list.
    variable_dim = len(data[0].shape)
    
    for key in kwargs.keys():
        if kwargs[key] is None:
            kwargs.pop(key)
    
    options = {}
    for key in plot_options.keys():
        options[key] = kwargs.pop(key, None)
            
    num_variables = len(data)
    
    if num_variables == 1:
        data = data[0]
    else:
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
    

    if plot_types[plot_type].expected_no_of_variables != num_variables:
        raise ex.InvalidPlotTypeError("The plot type is not valid for these variables")
    
    valrange = kwargs.pop("valrange", None)

    try:
        plot_types[plot_type].plot_method(data, *args, **kwargs)
    except KeyError:
        raise ex.InvalidPlotTypeError(plot_type)
    
    plt.ylim(**valrange)
        
    if options is not None:
        format_plot(data, options, plot_type)
      
    if out_filename is None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)        
