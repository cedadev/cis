'''
Module for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import iris.quickplot as qplt
import matplotlib.pyplot as plt

plot_options = { 'title' : plt.title,
              'xlabel' : plt.xlabel, 
              'ylabel' : plt.ylabel } 

class plot_type(object):
    def __init__(self, expected_no_of_variables, variable_dimensions, plot_method, is_map):
        self.expected_no_of_variables = expected_no_of_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        self.is_map = is_map
        
plot_types = {'line' : plot_type(1, 1, qplt.plot, False),
                'scatter' : plot_type(1, 2, qplt.points, False), 
                'heatmap' : plot_type(1, 2, qplt.pcolormesh, True),
                'contour' : plot_type(1, 2, qplt.contour, True),
                'contourf' : plot_type(1, 2, qplt.contourf, True)}

default_plot_types = { 1 : 'line',
                       2 : 'heatmap'}

def format_plot(data, options, plot_type):
    # If any of the options have not been specified, then use the defaults
    if options["title"] == None:
        options["title"] = ""
    if options["xlabel"] == None:
        for dim in xrange(len(data.shape)):
            for coord in data.coords(contains_dimension=dim, dim_coords=True):
                xlabel = coord.name()
        options["xlabel"] = xlabel.capitalize()
    if options["ylabel"] == None:
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
        
def plot(data, plot_type = None, out_filename = None, *args, **kwargs):
    '''
    Note: Data must be a list of cubes
    '''
    import jasmin_cis.exceptions as ex

    # Unpack the data list if there is only one element, otherwise the whole list
    # gets passed to the plot function. This could be done with unpacking in the 
    # plot method call but we already unpack the args list.
    variable_dim = len(data[0].shape)
    
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
    
    if plot_types[plot_type].expected_no_of_variables != num_variables:
        raise ex.InvalidPlotTypeError("The plot type is not valid for these variables")   
    
    try:
        plot_types[plot_type].plot_method(data, *args, **kwargs)
    except KeyError:
        raise ex.InvalidPlotTypeError(plot_type)
    
    format_plot(data, options, plot_type)
         
    if out_filename == None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)        
