#!/bin/env python
'''
Main driver script for the plotting tool
'''
from Plotting.Plotter import plot_line_graph, plot_heatmap, plot_scatter_graph
from Parser import parse_args
from Reading.DataReader import read_variable
from Exceptions.InvalidDimensionError import InvalidDimensionError

plot_types = {'line_plot' : plot_line_graph,
                'scatter' : plot_scatter_graph, 
                'heatmap' : plot_heatmap }

if __name__ ==  '__main__':
    main_arguments, plot_args = parse_args()
    
    try:
        data = read_variable(main_arguments.filenames, main_arguments.variable)
    except:
        pass
        # Think about what to catch here
    
    try:
        plot_types[main_arguments.type](data, main_arguments.output, *plot_args)
    except KeyError:
        print "Invalid plot type"
        exit(1)
    
    