'''
Module for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import iris.quickplot as qplt
import iris.plot as iplt
import matplotlib.pyplot as plt
import iris.coords
from cis import MAXIMUM_NUMBER_OF_VARIABLES

plot_options = { 'title' : plt.title,
              'xlabel' : plt.xlabel, 
              'ylabel' : plt.ylabel,
              'fontsize' : plt.rcParams.update } 

def unpack_cube(cube):
    import numpy as np
    from mpl_toolkits.basemap import addcyclic
    
    plot_defn = iplt._get_plot_defn(cube, iris.coords.POINT_MODE, ndims = 2)
    data = cube.data #ndarray
    if plot_defn.transpose:
        data = data.T
    
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
    
    if plot_defn.transpose:
        u = u.T
        v = v.T
    
    data, u = addcyclic(data, u)
    
    x, y = np.meshgrid(u, v)
    
    return data, x, y
    
def plot_scatter(cube, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    data, x, y = unpack_cube(cube) 
    basemap = Basemap()    
    basemap.points(x, y, data, latlon = True)

def plot_heatmap(cube, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    data, x, y = unpack_cube(cube) 
    basemap = Basemap()    
    basemap.pcolormesh(x, y, data, latlon = True)
    basemap.drawcoastlines()   
    
def plot_contour(cube, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    data, x, y = unpack_cube(cube) 
    basemap = Basemap()    
    basemap.contour(x, y, data, latlon = True)
    basemap.drawcoastlines()    
    
def plot_contourf(cube, *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    data, x, y = unpack_cube(cube) 
    basemap = Basemap()    
    basemap.contourf(x, y, data, latlon = True)
    basemap.drawcoastlines()  

class plot_type(object):
    def __init__(self, maximum_number_of_expected_no_of_variables, variable_dimensions, plot_method):
        self.maximum_number_of_expected_no_of_variables = maximum_number_of_expected_no_of_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        
plot_types = {'line' : plot_type(MAXIMUM_NUMBER_OF_VARIABLES, 1, qplt.plot),
                #'scatter' : plot_type(MAXIMUM_NUMBER_OF_VARIABLES, 2, qplt.points), 
                'scatter' : plot_type(MAXIMUM_NUMBER_OF_VARIABLES, 2, plot_scatter),
                #'heatmap' : plot_type(1, 2, qplt.pcolormesh),
                'heatmap' : plot_type(1, 2, plot_heatmap),
                #'contour' : plot_type(1, 2, qplt.contour),
                'contour' : plot_type(1, 2, plot_contour),
                #'contourf' : plot_type(1, 2, qplt.contourf)
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

def plot(cubes, plot_type = None, out_filename = None, *args, **kwargs):
    '''
    Note: Data must be a list of cubes
    This method needs commenting
    '''
    import jasmin_cis.exceptions as ex
    import logging
    
    kwargs = set_width_and_height(kwargs)    
    
    variable_dim = len(cubes[0].shape)
    
    for key in kwargs.keys():
        if kwargs[key] is None:
            kwargs.pop(key)
    
    options = {}
    for key in plot_options.keys():
        options[key] = kwargs.pop(key, None)
            
    num_variables = len(cubes)
    
    for cube in cubes:
        if len(cube.shape) != variable_dim:
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
    

    if num_variables > plot_types[plot_type].maximum_number_of_expected_no_of_variables:
        raise ex.InvalidPlotTypeError("The plot type is not valid for these variables")
    
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
        
    for i, cube in enumerate(cubes):
        # Temporarily add args to kwargs
        if plot_type == "line" and datafiles is not None:
            if datafiles[i]["linestyle"]:
                kwargs["linestyle"] = datafiles[i]["linestyle"]
            if datafiles[i]["color"]:
                kwargs["color"] = datafiles[i]["color"]
                
        plot_types[plot_type].plot_method(cube, *args, **kwargs)
        
        # Remove temp args
        if plot_type == "line" and datafiles is not None:
            if datafiles[i]["linestyle"]:
                kwargs.pop("linestyle")
            if datafiles[i]["color"]:
                kwargs.pop("color")
    
    if plot_type == "line" and valrange is not None:
        plt.ylim(**valrange)
        
    if options is not None:
        format_plot(cubes, options, plot_type, datafiles)
 
    if out_filename is None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)        
