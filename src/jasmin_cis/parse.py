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
    parser.add_argument("datafiles", metavar = "Input datafiles", nargs = "+", help = "The datafiles to be plotted, in the format: filename:variable:label:colour:style, where the last three arguments are optional")
    parser.add_argument("-v", "--variable", metavar = "Variable", nargs = "?", help = "The default variable to plot if not otherwise specified in the filename")
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")    
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type, one of: " + str(plot_types.keys()))
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")    
    parser.add_argument("--linewidth", metavar = "The line width", nargs = "?", help = "The width of the line")   
    parser.add_argument("--fontsize", metavar = "The font size", nargs = "?", help = "The size of the font")
    parser.add_argument("--cmap", metavar = "The colour map", nargs = "?", help = "The colour map used, e.g. RdBu")
    parser.add_argument("--height", metavar = "The height", nargs = "?", help = "The height of the plot in inches")
    parser.add_argument("--width", metavar = "The width", nargs = "?", help = "The width of the plot in inches")
    parser.add_argument("--valrange", metavar = "The range of values", nargs = "?", help = "The range of values to plot")
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
        
def parse_float(arg, name, parser):
    if arg:
        try:
            arg = float(arg)
        except ValueError:
            parser.error("'" + arg + "' is not a valid " + name)
    return arg

def check_filenames(filenames, parser):
    from collections import namedtuple
    overlay_plots = []
    OverlayOptions = namedtuple('OverlayOptions',['filename', "variable", "label", "color", "linestyle"])
    overlay_options = OverlayOptions(check_file_exists, check_nothing, check_nothing, check_color, check_line_style)
    
    for filename in filenames:
        split_filename = filename.split(":")
        overlay_plot = {}
        
        for i, option in enumerate(overlay_options._asdict().keys()):
            try:
                current_option = split_filename[i]
                if current_option:
                    overlay_options[i](current_option, parser) 
                    overlay_plot[option] = split_filename[i]
                else:
                    overlay_plot[option] = None
            except IndexError:
                overlay_plot[option] = None
        
        overlay_plots.append(overlay_plot)
    return overlay_plots

def check_variable(variable, overlay_plots, parser):
    if variable is None:
        raise_error = False
        if not overlay_plots:
            raise_error = True
        else:
            for overlay_plot in overlay_plots:
                if overlay_plot["variable"] is None:
                    raise_error = True
                    break
        if raise_error:
            parser.error("A variable must be specified")
    elif overlay_plots:
        for overlay_plot in overlay_plots:
            if overlay_plot["variable"] is None:
                overlay_plot["variable"] = variable
    return overlay_plots

def check_nothing(item, parser):
    pass

def check_plot_type(plot_type, variables, parser):
    # Check plot type is valid option for number of variables if specified
    if plot_type is not None:
        if plot_type in plot_types.keys():
            if plot_types[plot_type].expected_no_of_variables != len(variables):
                parser.error("Invalid number of variables for plot type")        
        else:        
            parser.error("'" + plot_type + "' is not a valid plot type, please use one of: " + str(plot_types.keys()))

def check_line_style(linestyle, parser):
    if linestyle not in line_styles:
        parser.error("'" + linestyle + "' is not a valid line style, please use one of: " + str(line_styles))   

def check_color(color, parser):
    if color is not None:
        from matplotlib.colors import cnames
        color = color.lower()
        if (color not in cnames) and color != "grey":
            parser.error("'" + color + "' is not a valid colour")   

def check_val_range(valrange, parser):
    if valrange is not None:
        if ":" in valrange:
            split_range = valrange.split(":")
            if len(split_range) == 2:
                ymin = parse_float(split_range[0], "min", parser)
                ymax = parse_float(split_range[1], "max", parser)
                valrange = {}
                if ymin:
                    valrange["ymin"] = ymin
                if ymax:
                    valrange["ymax"] = ymax
                if ymin and ymax and ymin > ymax:
                    parser.error("Range must be in the format 'min:max'")
            else:
                parser.error("Range must be in the format 'min:max'")
        else:
            parser.error("Range must be in the format 'min:max'")
    return valrange
                   
def validate_plot_args(arguments, parser):    
    arguments.datafiles = check_filenames(arguments.datafiles, parser)        
    arguments.datafiles = check_variable(arguments.variable, arguments.datafiles, parser)
    check_plot_type(arguments.type, arguments.variable, parser) 
    arguments.valrange = check_val_range(arguments.valrange, parser)
    # Try and parse numbers
    arguments.linewidth = parse_float(arguments.linewidth, "line width", parser)   
    arguments.fontsize = parse_float(arguments.fontsize, "font size", parser)
    arguments.height = parse_float(arguments.height, "height", parser)
    arguments.width = parse_float(arguments.width, "width", parser) 
    
    return arguments
                
def validate_info_args(arguments, parser):
    check_file_exists(arguments.filename, parser)
    return arguments

def validate_col_args(arguments, parser):
    check_file_exists(arguments.samplefilename, parser)
    
    for i, datafile in enumerate(arguments.datafiles):
        split_args = datafile.split(":")
        # Change this to only require the necessary amount of colons
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
