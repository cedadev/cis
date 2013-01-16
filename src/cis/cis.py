#!/bin/env python
'''
Main driver script for the Climate Intercomparison Suite
'''
from plot import plot
from parse import parse_args
from io.read import read_variable 
from exceptions import InvalidPlotTypeError, InvalidDimensionError

def plot_cmd(main_arguments):
    try:
        data = read_variable(main_arguments.filenames, main_arguments.variable)
    except:
        pass
        # Think about what to catch here
    
    try:
        plot(data, main_arguments.type, main_arguments.output, main_arguments.plot_args)
    except InvalidPlotTypeError:
        print "Please enter a valid plot type"
        exit(1)

def info_cmd(main_arguments):
    pass

commands = { 'plot' : plot_cmd,
             'info' : info_cmd}

if __name__ ==  '__main__':
    arguments = parse_args()
    commands[arguments.command](arguments)
    
    
