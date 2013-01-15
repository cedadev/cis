# Controller.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Controller module
import argparse
import sys
import os.path
import Controller

def initialise_parser():
    parser = argparse.ArgumentParser("Read and plot NetCDF files")    
    parser.add_argument("filenames", metavar = "Input filename(s)", nargs = "+", help = "The filename(s) of the file(s) to be plotted")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to plot")
    parser.add_argument("-o", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type")
    
    return parser

def parse_args(arguments = None):
    parser = initialise_parser()
    if (arguments == None):
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    args = parser.parse_args(arguments)   
    return args

def validate_args(args): 
    for filename in args.filenames:
        if not os.path.isfile(filename):
            print "'" + filename + "' cannot be found"
            exit(1)
    if (args.type != None) and not(args.type in Controller.chart_types):
        print "'" + args.type + "' is not a valid chart type"
        exit(1)
    if args.variables == None:
        print "At least one variable is required"
        exit(1)
    print "Successfully parsed"
    
args = parse_args(["/home/daniel/NetCDF Files/xglnwa.pm.k8dec-k9nov.vprof.tm.nc", "--type","heatmap"])
validate_args(args)
parse_args(["-h"])