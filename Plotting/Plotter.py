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
    
   
def plot_line_graph(data, out_filename = None, options = None, *args, **kwargs):
    iplt.plot(data, *args, **kwargs)      
    if options != None:
        for option, value in options.iteritems():
            try:
                plot_options[option](value)
            except KeyError:
                print "Invalid formatting option"
                # This should never be reached as the plot_options
                # should include all of the valid formatting options 
         
    show_or_save_plot(out_filename)
    
def plot_scatter_graph(data, out_filename = None, *args, **kwargs):        
    iplt.points(data, *args, **kwargs)   
    show_or_save_plot(out_filename)
    
def plot_heatmap(data, out_filename = None, *args, **kwargs):        
    iplt.pcolormesh(data, *args, **kwargs)   
    show_or_save_plot(out_filename)
     
def show_or_save_plot(out_filename = None):
    if out_filename == None:
        plt.show()  
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)
        
plot_types = {'line_plot' : plot_line_graph,
                'scatter' : plot_scatter_graph, 
                'heatmap' : plot_heatmap }   
   
def plot(data, type, out_filename = None, options = None, *args, **kwargs):
    from Exceptions.InvalidPlotTypeError import InvalidPlotTypeError
    
    try:
        plot_types[type](data, options, *args, **kwargs)
    except KeyError:
        raise InvalidPlotTypeError(type)
    
    if options != None:
        for option, value in options.iteritems():
            try:
                plot_options[option](value)
            except KeyError:
                print "Invalid formatting option"
                # This should never be reached as the plot_options
                # should include all of the valid formatting options 
         
    show_or_save_plot(out_filename)        