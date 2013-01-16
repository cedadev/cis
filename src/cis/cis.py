#!/bin/env python
'''
Main driver script for the Climate Intercomparison Suite
'''
from plot import plot
from parse import parse_args
from data_io.read import read_variable 

def plot_cmd(main_arguments):
    try:
        data = read_variable(main_arguments.filenames, main_arguments.variable)
    except:
        print "Data Error"
        exit(1)
        # Think about what to catch here
    
    plot(data, main_arguments.type, main_arguments.output, main_arguments.plot_args)

def info_cmd(main_arguments):
    pass

commands = { 'plot' : plot_cmd,
             'info' : info_cmd}

if __name__ ==  '__main__':
    arguments = parse_args()
    commands[arguments.command](arguments)
    
    
