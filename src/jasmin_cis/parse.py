'''
Module used for parsing
'''
import argparse
import sys
import os.path
from plot import plot_types

line_styles = ["solid", "dashed", "dashdot", "dotted"]

def initialise_top_parser():
    '''
    The parser to which all arguments are initially passed
    '''
    parser = argparse.ArgumentParser("CIS")
    subparsers = parser.add_subparsers(dest='command')
    plot_parser = subparsers.add_parser("plot", help = "Create plots")
    plot_parser = add_plot_parser_arguments(plot_parser)
    info_parser = subparsers.add_parser("info", help = "Get information about a file")
    info_parser = add_info_parser_arguments(info_parser)
    return parser

def add_plot_parser_arguments(parser):    
    parser.add_argument("filenames", metavar = "Input filename(s)", nargs = "+", help = "The filename(s) of the file(s) to be plotted")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to plot")
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")    
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type, one of: " + str(plot_types.keys()))
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")    
    parser.add_argument("--linestyle", metavar = "The line style", nargs = "?", default = "solid", help = "The style of the line, one of: " + str(line_styles))
    parser.add_argument("--color", metavar = "The line colour", nargs = "?", help = "The colour of the line")    
    return parser

def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar = "Filename", help = "The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to inspect")
    return parser

def validate_plot_args(arguments, parser):    
    # Check input files exist
    for filename in arguments.filenames:
        if not os.path.isfile(filename):
            parser.error("'" + filename + "' is not a valid filename")
    # Check at least one variable is specified        
    if arguments.variables == None:
        parser.error("At least one variable must be specified") 
    # Check plot type is valid option for number of variables if specified
    if (arguments.type != None):
        if (arguments.type in plot_types.keys()):
            if plot_types[arguments.type].expected_no_of_variables != len(arguments.variables):
                parser.error("Invalid number of variables for plot type")        
        else:        
            parser.error("'" + arguments.type + "' is not a valid plot type, please use one of: " + str(plot_types.keys()))
    
    if arguments.linestyle not in line_styles:
        parser.error("'" + arguments.linestyle + "' is not a valid line style, please use one of: " + str(line_styles))
        
    from matplotlib.colors import cnames
    arguments.color = arguments.color.lower()
    if (arguments.color not in cnames) and arguments.color != "grey":
        parser.error("'" + arguments.color + "' is not a valid colour")
        
        
def validate_info_args(arguments, parser):
    # Check file exists
    if not os.path.isfile(arguments.filename):
        parser.error("'" + arguments.filename + "' is not a valid filename")

def parse_args(arguments = None):
    '''
    Parse the arguments given. If no arguments are given, then used the command line arguments.
    '''
    parser = initialise_top_parser()
    if arguments == None:
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args = parser.parse_args(arguments)
    if main_args.command == 'plot':
        validate_plot_args(main_args, parser)
    elif main_args.command == 'info':
        validate_info_args(main_args, parser)
        
    return vars(main_args)
