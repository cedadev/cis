'''
Module used for parsing
'''
import argparse
import sys
import os.path
from plot import Plotter

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
    parser.add_argument("-v", "--variable", metavar = "Default variable", nargs = "?", help = "The default variable to plot if not otherwise specified in the filename")
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")    
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type, one of: " + str(Plotter.plot_types.keys()))
    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")    
    parser.add_argument("--itemwidth", metavar = "Item width", nargs = "?", help = "The width of the item")   
    parser.add_argument("--fontsize", metavar = "Font size", nargs = "?", help = "The size of the font")
    parser.add_argument("--cmap", metavar = "Colour map", nargs = "?", help = "The colour map used, e.g. RdBu")
    parser.add_argument("--height", metavar = "Plot height", nargs = "?", help = "The height of the plot in inches")
    parser.add_argument("--width", metavar = "Plot width", nargs = "?", help = "The width of the plot in inches")
    parser.add_argument("--xrange", metavar = "X range", nargs = "?", help = "The range of the x axis")
    parser.add_argument("--yrange", metavar = "Y range", nargs = "?", help = "The range of the y axis")
    parser.add_argument("--valrange", metavar = "Value range", nargs = "?", help = "The range of values to plot")
    parser.add_argument("--cbarorient", metavar = "Colour bar orientation", default = "horizontal", nargs = "?", help = "The orientation of the colour bar")
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
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")
    return parser

def check_file_exists(filename, parser):
    if not os.path.isfile(filename):
        parser.error("'" + filename + "' is not a valid filename")
        
def parse_float(arg, name, parser):
    '''
    Tries to parse a string as a float.
    
    @param arg:    The arg to parse as a float
    @param name:   A description of the argument used for error messages
    @param parser: The parser used to report an error message
    @return The parsed float if succeeds or the original argument if fails
    '''
    if arg:
        try:
            arg = float(arg)
            return arg
        except ValueError:
            parser.error("'" + arg + "' is not a valid " + name)
            return None

def check_datafiles(datafiles, parser):
    '''
    @param datafiles:    A list of datafiles (possibly containing colons)
    @param parser:       The parser used to report errors    
    @return The parsed datafiles as a list of dictionaries
    '''
    from collections import namedtuple
    DatafileOptions = namedtuple('DatafileOptions',['filename', "variable", "label", "color", "itemstyle"])
    datafile_options = DatafileOptions(check_file_exists, check_nothing, check_nothing, check_color, check_nothing)    
    
    return parse_colonic_arguments(datafiles, parser, datafile_options)

def parse_colonic_arguments(inputs, parser, options):
    '''
    @param inputs:    A list of strings, each in the format a:b:c:......:n where a,b,c,...,n are arguments
    @param parser:    The parser used to raise an error if one occurs
    @param options:   The possible options that each input can take. If no value is assigned to a particular option, then it is assigned None
    @return A list of dictionaries containing the parsed arguments
    '''
    input_dicts = []
    
    for input_string in inputs:
        split_input = input_string.split(":")
        input_dict = {}
        
        for i, option in enumerate(options._asdict().keys()):
            try:
                current_option = split_input[i]
                if current_option:
                    options[i](current_option, parser) 
                    input_dict[option] = split_input[i]
                else:
                    input_dict[option] = None
            except IndexError:
                input_dict[option] = None
        
        input_dicts.append(input_dict)
    return input_dicts

def check_variable(variable, datafiles, parser):
    '''
    Checks that a variable was specified, and assigns the default variable (if specified) to any datafiles with an unspecified variable
    '''
    if variable is None:
        raise_error = False
        if not datafiles:
            raise_error = True
        else:
            for datafile in datafiles:
                if datafile["variable"] is None:
                    raise_error = True
                    break
        if raise_error:
            parser.error("A variable must be specified")
    elif datafiles:
        for datafile in datafiles:
            if datafile["variable"] is None:
                datafile["variable"] = variable
    return datafiles

def check_nothing(item, parser):
    pass

def check_plot_type(plot_type, datafiles, parser):
    '''
    Checks plot type is valid option for number of variables if specified
    '''
    if plot_type is not None:
        if plot_type in Plotter.plot_types.keys():
            if Plotter.plot_types[plot_type].maximum_no_of_expected_variables < len(datafiles):
                parser.error("Invalid number of variables for plot type")        
        else:        
            parser.error("'" + plot_type + "' is not a valid plot type, please use one of: " + str(Plotter.plot_types.keys()))

def check_color(color, parser):
    if color is not None:
        from matplotlib.colors import cnames
        color = color.lower()
        if (color not in cnames) and color != "grey":
            parser.error("'" + color + "' is not a valid colour")   

def check_colour_bar_orientation(orientation, parser):
    orientation = orientation.lower()
    if orientation != "horizontal" and orientation != "vertical":
        parser.error("The legend orientation must either be horizontal or vertical")
    return orientation

def check_range(ax_range, parser, range_type):
    '''
    If a val range was specified, checks that they are valid numbers and the min is less than the max
    '''
    if ax_range is not None:
        if ":" in ax_range:
            split_range = ax_range.split(":")
            if len(split_range) == 2:
                r_min = parse_float(split_range[0], "min", parser)
                r_max = parse_float(split_range[1], "max", parser)
                ax_range = {}
                if r_min is not None:
                    ax_range[range_type + "min"] = r_min
                if r_max is not None:
                    ax_range[range_type + "max"] = r_max
                if r_min and r_max and r_min > r_max:
                    parser.error("Range must be in the format 'min:max'")
            else:
                parser.error("Range must be in the format 'min:max'")
        else:
            parser.error("Range must be in the format 'min:max'")
    return ax_range
                   
def validate_plot_args(arguments, parser): 
    arguments.datafiles = check_datafiles(arguments.datafiles, parser)        
    arguments.datafiles = check_variable(arguments.variable, arguments.datafiles, parser)
    check_plot_type(arguments.type, arguments.datafiles, parser) 
    arguments.valrange = check_range(arguments.valrange, parser, "v")
    arguments.xrange = check_range(arguments.xrange, parser, "x")
    arguments.yrange = check_range(arguments.yrange, parser, "y")
    arguments.cbarorient = check_colour_bar_orientation(arguments.cbarorient, parser)
    # Try and parse numbers
    arguments.itemwidth = parse_float(arguments.itemwidth, "item width", parser)   
    arguments.fontsize = parse_float(arguments.fontsize, "font size", parser)
    arguments.height = parse_float(arguments.height, "height", parser)
    arguments.width = parse_float(arguments.width, "width", parser) 
    
    return arguments
                
def validate_info_args(arguments, parser):
    check_file_exists(arguments.filename, parser)
    return arguments

def check_valid_col_method(method_name, parser):
    '''
        Check that if a co-location method is specified that it is a valid option
    '''
    from col import Colocator
    if method_name and method_name not in Colocator.ColocationTechniques._fields:
        parser.error("'" + method_name + "' is not a valid co-location method")

def validate_col_args(arguments, parser):
    '''
    Checks that the filenames are valid and that variables and methods have been specified.
    Assigns default method/variable to datafiles with unspecified method/variable if default is specified
    '''
    from collections import namedtuple
    
    check_file_exists(arguments.samplefilename, parser)
    
    check_valid_col_method(arguments.method, parser)
    
    if not arguments.output:
        parser.error("Please specify an output file using the -o flag")
    
    DatafileOptions = namedtuple('ColocateOptions',['filename', "variable", "method"])
    datafile_options = DatafileOptions(check_file_exists, check_nothing, check_valid_col_method)    
    
    arguments.datafiles =  parse_colonic_arguments(arguments.datafiles, parser, datafile_options)
    for datafile in arguments.datafiles:
        if not datafile["variable"]:
            if arguments.variable:
                datafile["variable"] = arguments.variable
            else:
                parser.error("Please enter a valid colocation variable for each datafile, or specify a default variable")
        if not datafile["method"]:
            if arguments.method:
                datafile["method"] = arguments.method
            else:
                parser.error("Please enter a valid colocation method for each datafile, or specify a default method")
    
    return arguments

validators = { 'plot' : validate_plot_args,
               'info' : validate_info_args,
               'col'  : validate_col_args}

def parse_args(arguments = None):
    '''
    Parse the arguments given. If no arguments are given, then used the command line arguments.
    Returns a dictionary contains the parsed arguments
    '''
    parser = initialise_top_parser()
    if arguments is None:
        #sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args = parser.parse_args(arguments)
    main_args = validators[main_args.command](main_args, parser)
        
    return vars(main_args)
