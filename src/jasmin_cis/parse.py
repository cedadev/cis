# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module used for parsing
import argparse
import sys
import os.path

def initialise_top_parser():
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
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type")    
    return parser

def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar = "Filename", help = "The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to inspect")
    return parser
    
def initialise_plot_format_parser():
    parser = argparse.ArgumentParser("Read and plot NetCDF files")
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")
    return parser

def parse_plot_format_args(arguments):
    parser = initialise_plot_format_parser()
    return parser.parse_args(arguments)

def validate_plot_args(arguments, parser):
    from plot import plot_types
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
            parser.error("'" + arguments.type + "' is not a valid plot type")
        
def validate_info_args(arguments, parser):
    if not os.path.isfile(arguments.filename):
        parser.error("'" + arguments.filename + "' is not a valid filename")

def parse_args(arguments = None):
    parser = initialise_top_parser()
    if arguments == None:
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args, remaining_arguments = parser.parse_known_args(arguments)
    if main_args.command == 'plot':
        #if len(remaining_arguments) != 0:
            # Read off the main arguments and any keywords that aren't recognised are passed to the plot parser
        main_args.plot_format_args = vars(parse_plot_format_args(remaining_arguments))
        #else:
         #   main_args.plot_format_args = None
        validate_plot_args(main_args, parser)
    elif main_args.command == 'info':
        validate_info_args(main_args, parser)
        
    return main_args

#args, p_args = parse_args(["/home/shared/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc","--type","heatmap", "-v", "rain","--title", "test"])
#print args, p_args
#print vars(args)
#print vars(p_args)
