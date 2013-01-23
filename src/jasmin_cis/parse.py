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
    col_parser = subparsers.add_parser("col", help = "Perform colocation")
    col_parser = add_col_parser_arguments(col_parser)
    return parser

def add_plot_parser_arguments(parser):    
    parser.add_argument("filenames", metavar = "Input filename(s)", nargs = "+", help = "The filename(s) of the file(s) to be plotted")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to plot")
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")    
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type, one of: " + str(plot_types.keys()))
    parser.add_argument("-x", "--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("-y", "--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")    
    parser.add_argument("--linestyle", metavar = "The line style", nargs = "?", default = "solid", help = "The style of the line, one of: " + str(line_styles))
    parser.add_argument("--linewidth", metavar = "The line width", nargs = "?", help = "The width of the line")
    parser.add_argument("--color", metavar = "The line colour", nargs = "?", help = "The colour of the line")    
    parser.add_argument("--fontsize", metavar = "The font size", nargs = "?", help = "The size of the font")
    parser.add_argument("--cmap", metavar = "The colour map", nargs = "?", help = "The colour map used, e.g. RdBu")
    return parser

def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar = "Filename", help = "The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to inspect")
    return parser

def add_col_parser_arguments(parser):
    parser.add_argument("samplefilename", metavar = "SampleFilename", help = "The filename of the sample file")
    parser.add_argument("datafiles", metavar = "DataFiles", nargs = "+", help = "Files to colocate with variable names and other options split by a colon")
    parser.add_argument("-v", "--variable", metavar = "DefaultVariable", nargs = "?", help = "The default variable to use for the data files unless explicitly overridden")
    parser.add_argument("-m", "--method", metavar = "DefaultMethod", nargs = "?", help = "The default method to use for the data files unless explicitly overridden")
    return parser

def check_file_exists(filename, parser):
    if not os.path.isfile(filename):
        parser.error("'" + filename + "' is not a valid filename")
        
def validate_plot_args(arguments, parser):    
    for filename in arguments.filenames:
        check_file_exists(filename, parser)
    # Check at least one variable is specified        
    if arguments.variables is None:
        parser.error("At least one variable must be specified") 
    # Check plot type is valid option for number of variables if specified
    if (arguments.type is not None):
        if (arguments.type in plot_types.keys()):
            if plot_types[arguments.type].expected_no_of_variables != len(arguments.variables):
                parser.error("Invalid number of variables for plot type")        
        else:        
            parser.error("'" + arguments.type + "' is not a valid plot type, please use one of: " + str(plot_types.keys()))
    
    if arguments.linestyle not in line_styles:
        parser.error("'" + arguments.linestyle + "' is not a valid line style, please use one of: " + str(line_styles))
    
    if arguments.linewidth is not None:
        try:
            float(arguments.linewidth)
        except ValueError:
            parser.error("'" + arguments.linewidth + "' is not a valid line width")
        
    if arguments.color is not None:
        from matplotlib.colors import cnames
        arguments.color = arguments.color.lower()
        if (arguments.color not in cnames) and arguments.color != "grey":
            parser.error("'" + arguments.color + "' is not a valid colour")
        
    if arguments.fontsize is not None:
        try:
            float(arguments.fontsize)
        except ValueError:
            parser.error("'" + arguments.fontsize + "' is not a valid font size")
    return arguments
                
def validate_info_args(arguments, parser):
    check_file_exists(arguments.filename, parser)
    return arguments

def validate_col_args(arguments, parser):
    check_file_exists(arguments.samplefilename, parser)
    
    for i, datafile in enumerate(arguments.datafiles):
        split_args = datafile.split(":")
        if len(split_args) == 3:    
            split_args = {"filename" : split_args[0],
                          "variable" : split_args[1],
                          "method"   : split_args[2]}
                
            check_file_exists(split_args["filename"], parser)
            
            if not split_args["variable"] and arguments.variable is not None:
                split_args["variable"] = arguments.variable
                
            if not split_args["method"] and arguments.method is not None:
                split_args["method"] = arguments.method
            
            arguments.datafiles[i] = split_args
        else:
            parser.error("Data files must be of the format dataf:var:method, where var and method are optional, but the colons are required")
    
    return arguments

validators = { 'plot' : validate_plot_args,
               'info' : validate_info_args,
               'col'  : validate_col_args}

def parse_args(arguments = None):
    '''
    Parse the arguments given. If no arguments are given, then used the command line arguments.
    '''
    parser = initialise_top_parser()
    if arguments is None:
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args = parser.parse_args(arguments)
    main_args = validators[main_args.command](main_args, parser)
        
    return vars(main_args)
