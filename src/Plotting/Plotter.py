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
        
plot_types = {'line_plot' : iplt.plot,
                'scatter' : iplt.points, 
                'heatmap' : iplt.pcolormesh }   
   
def plot(data, plot_type, out_filename = None, options = None, *args, **kwargs):
    from Exceptions.InvalidPlotTypeError import InvalidPlotTypeError
    
    try:
        plot_types[plot_type](data, *args, **kwargs)
    except KeyError:
        raise InvalidPlotTypeError(plot_type)
    
    if options != None:
        for option, value in options.iteritems():
            try:
                plot_options[option](value)
            except KeyError:
                print "Invalid formatting option"
                # This should never be reached as the plot_options
                # should include all of the valid formatting options 
         
    if out_filename == None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)        