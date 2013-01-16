# Parser.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module used for parsing
import argparse
import sys
import os.path
import Controller

def initialise_parser():
    parser = argparse.ArgumentParser("Read and plot NetCDF files")    
    parser.add_argument("filenames", metavar = "Input filename(s)", nargs = "+", help = "The filename(s) of the file(s) to be plotted")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to plot")
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type")    
    return parser
    
def initialise_plot_parser():
    parser = argparse.ArgumentParser("Read and plot NetCDF files")
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")
    return parser

def parse_plot_args(arguments):
    parser = initialise_plot_parser()
    return parser.parse_args(arguments)

def parse_args(arguments = None):
    parser = initialise_parser()
    if arguments == None:
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args, remaining_arguments = parser.parse_known_args(arguments)
    # Read off the main arguments and any keywords that aren't recognised are passed to the plot parser
    plot_args = parse_plot_args(remaining_arguments)
    for filename in main_args.filenames:
        if not os.path.isfile(filename):
            parser.error("Please enter a valid filename")
    if (main_args.type != None) and not(main_args.type in Controller.chart_types):        
        parser.error("Please enter a valid plot type")
    if main_args.variables == None:
        parser.error("At least one variable must be specified")
    return main_args, plot_args

args, p_args = parse_args(["/home/shared/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc","--type","heatmap", "-v", "rain","--title", "test"])
print args, p_args
print vars(args)
print vars(p_args)
