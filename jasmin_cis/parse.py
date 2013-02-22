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
    add_plot_parser_arguments(plot_parser)
    info_parser = subparsers.add_parser("info", help = "Get information about a file")
    add_info_parser_arguments(info_parser)
    col_parser = subparsers.add_parser("col", help = "Perform colocation")
    add_col_parser_arguments(col_parser)
    return parser

def add_plot_parser_arguments(parser):    
    parser.add_argument("datagroups", metavar = "Input datagroups", nargs = "+", help = "The datagroups to be plotted, in the format: variable:filenames:colour:style:label, where the last three arguments are optional")
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
    parser.add_argument("--nocolourbar", metavar = "Hides the colour bar", default = "False", nargs = "?", help = "Does not show the colour bar")
    parser.add_argument("--logx", metavar = "Log (base 10) scale on X axis", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the x axis")
    parser.add_argument("--logy", metavar = "Log (base 10) scale on Y axis", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the y axis")
    parser.add_argument("--logv", metavar = "Log (base 10) scale for values", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the colour bar")
    parser.add_argument("--grid", metavar = "Show grid", default = "False", nargs = "?", help = "Shows a grid on a line graph")
    return parser

def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar = "Filename", help = "The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to inspect")
    return parser

def add_col_parser_arguments(parser):
    parser.add_argument("samplefilename", metavar = "SampleFilename", help = "The filename of the sample file")
    parser.add_argument("datagroups", metavar = "DataGroups", nargs = "+", help = "Variable to colocate with filenames and other options split by a colon")
    parser.add_argument("--constraint", metavar = "DefaultConstraint", nargs = "?", help = "The default constraint to use for the data groups unless explicitly overridden")
    parser.add_argument("--kernel", metavar = "DefaultKernel", nargs = "?", help = "The default method to use for the data files unless explicitly overridden")
    parser.add_argument("--colocator", metavar = "DefaultColocator", nargs = "?", help = "The default method to use for the data files unless explicitly overridden")
    parser.add_argument("-o", "--output", metavar = "Output filename", default = "out", nargs = "?", help = "The filename of the output file for the plot image")
    return parser

def expand_file_list(filenames, parser):
    '''

    @param filenames: A string which is a comma seperated list of filenames, wildcarded filenames or directories
    @param parser: A reference parser for raising errors on
    @return: A flat list of files which exist
    '''
    from glob import glob
    if not filenames:
        parser.error("Please specify at least one filename")
    input_list = filenames.split(',')
    file_list = []
    for element in input_list:
        if any(wildcard in element for wildcard in ['*', '?']):
            file_list += glob(element)
        elif os.path.isdir(element):
            [ file_list.append(os.path.join(element,a_file)) for a_file in os.listdir(element) if os.path.isfile(a_file) ]
        elif os.path.isfile(element):
            file_list.append(element)
        else:
            parser.error("'" + element + "' is not a valid filename")
    return file_list

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

def get_plot_datagroups(datagroups, parser):
    '''
    @param datagroups:    A list of datagroups (possibly containing colons)
    @param parser:       The parser used to report errors    
    @return The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple
    DatagroupOptions = namedtuple('DatagroupOptions',[ "variable", "filenames", "color", "itemstyle", "label"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, check_color, check_nothing, check_nothing)
    
    return parse_colonic_arguments(datagroups, parser, datagroup_options, min_args=2)


def get_col_datagroups(datagroups, parser):
    '''
    @param datagroups:    A list of datagroups (possibly containing colons)
    @param parser:       The parser used to report errors
    @return The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple
    from utils import parse_key_val_list
    DatagroupOptions = namedtuple('DatagroupOptions',["variable", "filenames", "colocator", "constraint", "kernel"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, parse_key_val_list, parse_key_val_list, parse_key_val_list)

    return parse_colonic_arguments(datagroups, parser, datagroup_options, min_args=2)


def parse_colonic_arguments(inputs, parser, options, min_args=1):
    '''
    @param inputs:    A list of strings, each in the format a:b:c:......:n where a,b,c,...,n are arguments
    @param parser:    The parser used to raise an error if one occurs
    @param options:   The possible options that each input can take. If no value is assigned to a particular option, then it is assigned None
    @param min_args:   The minimum number of arguments to expect - we can't say which arguments are compulsory, just how many are
    @return A list of dictionaries containing the parsed arguments
    '''
    input_dicts = []
    
    for input_string in inputs:
        split_input = input_string.split(":")
        if len(split_input) < min_args:
            parser.error("A mandatory data group option is missing")
        input_dict = {}
        
        for i, option in enumerate(options._asdict().keys()):
            try:
                current_option = split_input[i]
                input_dict[option] = options[i](current_option, parser)
            except IndexError:
                input_dict[option] = None
        
        input_dicts.append(input_dict)
    return input_dicts

def apply_default_values(datagroups, variable, default_val):
    '''
    Checks each datagroup for the the given variable, if it is empty either apply the default value or raise an error

    @param datagroups: A list of datagroups
    @param variable: The variable to check
    @param default_val: The default value to apply
    @return: An updated list of datagroups with defaults applied

    @raise InvalidCommandLineOptionError
    '''
    from jasmin_cis.exceptions import InvalidCommandLineOptionError
    for datafile in datagroups:
        if datafile[variable] is None:
            if default_val is not None:
                datafile[variable] = default_val
            else:
                raise InvalidCommandLineOptionError
    return datagroups

def check_nothing(item, parser):
    return item

def check_is_not_empty(item, parser):
    if not item:
        parser.error("Non optional argument not specified in datagroup")
    return item

def check_plot_type(plot_type, datagroups, parser):
    '''
    Checks plot type is valid option for number of variables if specified
    '''

    if plot_type is not None:
        if plot_type not in Plotter.plot_types.keys():
            parser.error("'" + plot_type + "' is not a valid plot type, please use one of: " + str(Plotter.plot_types.keys()))

def check_color(color, parser):
    if color:
        from matplotlib.colors import cnames
        color = color.lower()
        if (color not in cnames) and color != "grey":
            parser.error("'" + color + "' is not a valid colour")
    else:
        color = None
    return color

def check_colour_bar_orientation(orientation, parser):
    orientation = orientation.lower()
    if orientation != "horizontal" and orientation != "vertical":
        parser.error("The colour bar orientation must either be horizontal or vertical")
    return orientation

def check_range(ax_range, parser, range_type):
    '''
    If a val range was specified, checks that they are valid numbers and the min is less than the max
    '''
    error_message = "Range must be in the format 'min:max:stepsize'"
    if ax_range is not None:
        if ":" in ax_range:
            split_range = ax_range.split(":")
            if len(split_range) == 2 or len(split_range) == 3:
                r_min = parse_float(split_range[0], "min", parser)
                r_max = parse_float(split_range[1], "max", parser)
                ax_range = {}
                if r_min is not None:
                    ax_range[range_type + "min"] = r_min
                if r_max is not None:
                    ax_range[range_type + "max"] = r_max
                if r_min and r_max and r_min > r_max:
                    parser.error(error_message)
                if len(split_range) == 3:
                    r_step = parse_float(split_range[2], "step", parser)
                    if r_step is not None:
                        ax_range[range_type + "step"] = r_step
            else:
                parser.error(error_message)
        else:
            parser.error(error_message)
    return ax_range

def check_boolean_argument(argument):
    if argument is None or argument != "False":
        return True
    else:
        return False
    
def assign_logs(arguments):
    arguments.logx = check_boolean_argument(arguments.logx)
    arguments.logy = check_boolean_argument(arguments.logy)
    arguments.logv = check_boolean_argument(arguments.logv)
    
    if arguments.logx:
        arguments.logx = 10
    else:
        arguments.logx = None
        
    if arguments.logy:
        arguments.logy = 10
    else:
        arguments.logy = None

    if arguments.logv:
        arguments.logv = 10
    else:
        arguments.logv = None
    
    return arguments

def validate_plot_args(arguments, parser): 
    arguments.datagroups = get_plot_datagroups(arguments.datagroups, parser)
    check_plot_type(arguments.type, arguments.datagroups, parser) 
    arguments.valrange = check_range(arguments.valrange, parser, "v")
    arguments.xrange = check_range(arguments.xrange, parser, "x")
    arguments.yrange = check_range(arguments.yrange, parser, "y")
    arguments.cbarorient = check_colour_bar_orientation(arguments.cbarorient, parser)
    arguments.nocolourbar = check_boolean_argument(arguments.nocolourbar)
    arguments.grid = check_boolean_argument(arguments.grid)
    
    arguments = assign_logs(arguments)
    # Try and parse numbers
    arguments.itemwidth = parse_float(arguments.itemwidth, "item width", parser)   
    arguments.fontsize = parse_float(arguments.fontsize, "font size", parser)
    arguments.height = parse_float(arguments.height, "height", parser)
    arguments.width = parse_float(arguments.width, "width", parser) 
    
    return arguments
                
def validate_info_args(arguments, parser):
    check_file_exists(arguments.filename, parser)
    return arguments

def validate_col_args(arguments, parser):
    '''
    Checks that the filenames are valid and that variables and methods have been specified.
    Assigns default method/variable to datagroups with unspecified method/variable if default is specified
    '''

    arguments.datagroups = get_col_datagroups(arguments.datagroups, parser)

    arguments.datagroups = apply_default_values(arguments.datagroups, 'colocator', arguments.colocator)
    arguments.datagroups = apply_default_values(arguments.datagroups, 'constraint', arguments.constraint)
    arguments.datagroups = apply_default_values(arguments.datagroups, 'kernel', arguments.kernel)

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
