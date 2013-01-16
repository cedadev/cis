#!/bin/env python
'''
Main driver script for the plotting tool
'''
from plot import plot
from parse import parse_args
from io.read import read_variable 
from exceptions import InvalidPlotTypeError, InvalidDimensionError

if __name__ ==  '__main__':
    main_arguments, plot_args = parse_args()
    
    try:
        data = read_variable(main_arguments.filenames, main_arguments.variable)
    except:
        pass
        # Think about what to catch here
    
    try:
        plot(data, main_arguments.type, main_arguments.output, plot_args)
    except InvalidPlotTypeError:
        print "Please enter a valid plot type"
        exit(1)