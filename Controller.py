# Controller.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Controller module
import iris
import argparse
import sys

def get_number_of_variables(file):
    return len(file)

def initialise_parser():
    parser = argparse.ArgumentParser("Read and plot NetCDF files.")
    parser.add_argument("filename", metavar = "Input filename", nargs = "+", help = "The filename of the file to be plotted")
    parser.add_argument("-o", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to plot")
    return parser

def parse_args():
    parser = initialise_parser()
    args = parser.parse_args(sys.argv)
    
    
parse_args()