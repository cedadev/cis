# Plotter.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Class for plotting graphs

import iris.plot as iplt
import matplotlib.pyplot as plt

plot_options = { 'title' : plt.title,
              'xlabel' : plt.xlabel, 
              'ylabel' : plt.ylabel } 

class plot_type(object):
    def __init__(self, expected_no_of_variables, variable_dimensions, plot_method):
        self.expected_no_of_variables = expected_no_of_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method
        
plot_types = {'line' : plot_type(1, 1, iplt.plot),
                'scatter' : plot_type(1, 2, iplt.points), 
                'heatmap' : plot_type(1, 2, iplt.pcolormesh),
                'contour' : plot_type(1, 2, iplt.contour),
                'contourf' : plot_type(1, 2, iplt.contourf)}

default_plot_types = { 1 : 'line',
                       2 : 'heatmap'}
   
def plot(data, plot_type = None, out_filename = None, options = None, *args, **kwargs):
    #from jasmin_cis.exceptions import InvalidPlotTypeError, InconsistentDimensionsError
    import jasmin_cis.exceptions as ex

    # Unpack the data list if there is only one element, otherwise the whole list
    #  gets passed to the plot function. This could be done with unpacking in the 
    #  plot method call but we already unpack the args list.
    variable_dim = len(data[0].shape)
    if len(data) == 1:
        data = data[0]
    else:
        for item in data:
            if len(item.shape) != variable_dim:
                raise ex.InconsistentDimensionsError("Number of "
                    "dimensions must be consistent across variables")
        
    if plot_type is None:
        try:
            plot_type = default_plot_types[variable_dim]
        except KeyError:
            raise ex.InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")
    elif plot_types[plot_type].variable_dimensions != variable_dim:
        raise ex.InvalidPlotTypeError("The plot type is not valid for this variable, the dimensions do not match")
    
    try:
        plot_types[plot_type].plot_method(data, *args, **kwargs)
    except KeyError:
        raise ex.InvalidPlotTypeError(plot_type)
    
    if options != None:
        for option, value in options.iteritems():
            try:
                plot_options[option](value)
            except KeyError:
                raise ex.InvalidPlotFormatError("Invalid formatting option")
                # This should never be reached as the plot_options
                # should include all of the valid formatting options
         
    if out_filename == None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)        