'''
Module used for parsing
'''
import argparse
import sys
import os.path
from plotting.plot import Plotter
import logging

def initialise_top_parser():
    '''
    The parser to which all arguments are initially passed
    '''
    parser = argparse.ArgumentParser("cis")
    subparsers = parser.add_subparsers(dest='command')
    plot_parser = subparsers.add_parser("plot", help = "Create plots")
    add_plot_parser_arguments(plot_parser)
    info_parser = subparsers.add_parser("info", help = "Get information about a file")
    add_info_parser_arguments(info_parser)
    col_parser = subparsers.add_parser("col", help = "Perform colocation")
    add_col_parser_arguments(col_parser)
    return parser


def add_plot_parser_arguments(parser):

    from jasmin_cis.data_io.products.AProduct import AProduct
    import jasmin_cis.plugin as plugin
    product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products.products', verbose=False)

    parser.add_argument("datagroups", metavar = "Input datagroups", nargs = "+",
                        help = "The datagroups to be plotted, in the format: variable:filenames:colour:style:label:product, where the last four arguments are optional, colour is any valid html colour (e.g. red) and product is one of " + str([cls().__class__.__name__ for cls in product_classes]))
    parser.add_argument("-o", "--output", metavar = "Output filename", nargs = "?", help = "The filename of the output file for the plot image")
    parser.add_argument("--type", metavar = "Chart type", nargs = "?", help = "The chart type, one of: " + str(Plotter.plot_types.keys()))

    parser.add_argument("--xlabel", metavar = "X axis label", nargs = "?", help = "The label for the x axis")
    parser.add_argument("--ylabel", metavar = "Y axis label", nargs = "?", help = "The label for the y axis")
    parser.add_argument("--cbarlabel", metavar = "Colour bar label", nargs = "?", help = "The label for the colour bar")

    parser.add_argument("--xtickangle", metavar = "X tick angle", nargs = "?", help = "The angle (in degrees) of the ticks on the x axis")
    parser.add_argument("--ytickangle", metavar = "Y tick angle", nargs = "?", help = "The angle (in degrees) of the ticks on the y axis")

    parser.add_argument("--title", metavar = "Chart title", nargs = "?", help = "The title for the chart")    
    parser.add_argument("--itemwidth", metavar = "Item width", nargs = "?", help = "The width of an item. Unit are points in the case of a line, and point^2 in the case of a scatter point.")
    parser.add_argument("--fontsize", metavar = "Font size", nargs = "?", help = "The size of the font in points")
    parser.add_argument("--cmap", metavar = "Colour map", nargs = "?", help = "The colour map used, e.g. RdBu")
    parser.add_argument("--height", metavar = "Plot height", nargs = "?", help = "The height of the plot in inches")
    parser.add_argument("--width", metavar = "Plot width", nargs = "?", help = "The width of the plot in inches")

    parser.add_argument("--xmin", metavar = "Minimum x", nargs = "?", help = "The minimum x value to plot")
    parser.add_argument("--xmax", metavar = "Maximum x", nargs = "?", help = "The maximum x value to plot")
    parser.add_argument("--xstep", metavar = "X step", nargs = "?", help = "The step of the x axis")

    parser.add_argument("--ymin", metavar = "Minimum y", nargs = "?", help = "The minimum y value to plot")
    parser.add_argument("--ymax", metavar = "Maximum y", nargs = "?", help = "The maximum y value to plot")
    parser.add_argument("--ystep", metavar = "Y step", nargs = "?", help = "The step of the y axis")

    parser.add_argument("--vmin", metavar = "Minimum value", nargs = "?", help = "The minimum value to plot")
    parser.add_argument("--vmax", metavar = "Maximum value", nargs = "?", help = "The maximum value to plot")
    parser.add_argument("--vstep", metavar = "X value", nargs = "?", help = "The step of the colour bar")

    parser.add_argument("--xbinwidth", metavar = "Histogram x axis bin width", nargs = "?", help = "The width of the bins on the x axis of a histogram")
    parser.add_argument("--ybinwidth", metavar = "Histogram y axis bin width", nargs = "?", help = "The width of the bins on the y axis of a histogram")

    parser.add_argument("--cbarorient", metavar = "Colour bar orientation", default = "vertical", nargs = "?", help = "The orientation of the colour bar, either horizontal or vertical")
    parser.add_argument("--nocolourbar", metavar = "Hides the colour bar", default = "False", nargs = "?", help = "Does not show the colour bar")

    parser.add_argument("--logx", metavar = "Log (base 10) scale on X axis", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the x axis")
    parser.add_argument("--logy", metavar = "Log (base 10) scale on Y axis", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the y axis")
    parser.add_argument("--logv", metavar = "Log (base 10) scale for values", default = "False", nargs = "?", help = "Uses a log scale (base 10) on the colour bar")

    parser.add_argument("--grid", metavar = "Show grid", default = "False", nargs = "?", help = "Shows grid lines on the plot")
    parser.add_argument("--xaxis", metavar = "Variable on x axis", nargs="?", help="Name of variable to use on the x axis")
    parser.add_argument("--yaxis", metavar = "Variable on y axis", nargs="?", help="Name of variable to use on the y axis")

    parser.add_argument("--coastlinescolour", metavar = "Coastlines Colour", nargs = "?", help = "The colour of the coastlines on a map. Any valid html colour (e.g. red)")
    return parser


def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar = "Filename", help = "The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar = "Variable(s)", nargs = "+", help = "The variable(s) to inspect")
    parser.add_argument("--type", metavar = "type of HDF data", nargs="?", help="Can be 'VD' or 'SD'. Use 'All' for both.")
    return parser


def add_col_parser_arguments(parser):
    parser.add_argument("samplegroup", metavar = "SampleGroup", help = "A string of the format filename:variable:product where the variable and product are optional")
    parser.add_argument("datagroups", metavar = "DataGroups", nargs = "+", help = "Variable to colocate with filenames and other options split by a colon")
    parser.add_argument("-o", "--output", metavar = "Output filename", default = "out", nargs = "?", help = "The filename of the output file for the plot image")
    return parser


def expand_file_list(filenames, parser):
    '''

    @param filenames: A string which is a comma seperated list of filenames, wildcarded filenames or directories
    @param parser: A reference parser for raising errors on
    @return: A flat list of files which exist - with no duplicate
    '''
    from glob import glob
    from jasmin_cis.utils import OrderedSet
    if not filenames:
        parser.error("Please specify at least one filename")
    input_list = filenames.split(',')

    # Ensure we don't get duplicates by making file_set a set
    file_set = OrderedSet()
    for element in input_list:
        if any(wildcard in element for wildcard in ['*', '?',']','}']):
            filenames = glob(element)
            filenames.sort()
            for filename in filenames:
                file_set.add(filename)
        elif os.path.isdir(element):
            filenames = os.listdir(element)
            filenames.sort()
            for a_file in filenames:
                full_file = os.path.join(element, a_file)
                if os.path.isfile(full_file):
                    file_set.add(full_file)
        elif os.path.isfile(element):
            file_set.add(element)
        else:
            parser.error("'" + element + "' is not a valid filename")

    # Check we matched at least one file
    if not file_set:
        parser.error("No files found which match: " + str(filenames))

    # Cast set to a list to make it easier to index etc. later on
    alist = list(file_set)

    logging.info("Identified input file list: " + str(alist))

    return alist


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

def check_product(product, parser):
    from jasmin_cis.data_io.products.AProduct import AProduct
    import jasmin_cis.plugin as plugin
    if product:
        product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products.products')
        product_names = [cls().__class__.__name__ for cls in product_classes]
        if product not in product_names:
            parser.error(product + " is not a valid product. Please use one of " + str(product_names))
    else:
        product = None
    return product

def get_plot_datagroups(datagroups, parser):
    '''
    @param datagroups:    A list of datagroups (possibly containing colons)
    @param parser:       The parser used to report errors    
    @return The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple
    DatagroupOptions = namedtuple('DatagroupOptions',[ "variable", "filenames", "color", "itemstyle", "label", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, check_color, check_nothing, check_nothing, check_product)
    return parse_colonic_arguments(datagroups, parser, datagroup_options, min_args=2)


def get_col_datagroups(datagroups, parser):
    '''
    @param datagroups:    A list of datagroups (possibly containing colons)
    @param parser:       The parser used to report errors
    @return The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple
    DatagroupOptions = namedtuple('DatagroupOptions',["variable", "filenames", "colocator", "constraint", "kernel", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, extract_method_and_args, extract_method_and_args, extract_method_and_args, check_product)

    return parse_colonic_arguments(datagroups, parser, datagroup_options, min_args=2)


def get_col_samplegroup(samplegroup, parser):
    '''
    @param samplegroups:    A list of datagroups (possibly containing colons)
    @param parser:       The parser used to report errors
    @return The parsed samplegroups as a list of dictionaries
    '''
    from collections import namedtuple
    DatagroupOptions = namedtuple('SamplegroupOptions',[ "filenames", "variable", "product"])
    samplegroup_options = DatagroupOptions(expand_file_list, check_nothing, check_product)

    return parse_colonic_arguments(samplegroup, parser, samplegroup_options)


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


def extract_method_and_args(arguments, parser):
    from jasmin_cis.utils import parse_key_val_list
    if not arguments:
        method_and_args = None
    else:
        elements = arguments.split(',')
        method_name = elements[0]
        args = elements[1:] if len(elements) > 1 else []
        method_and_args = ( method_name, parse_key_val_list(args) )
    return method_and_args


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

def parse_as_float_or_date(arg, name, parser):
    from time_util import parse_datetimestr_to_std_time
    if arg:
        try:
            # First try and parse as a float
            arg = float(arg)
        except ValueError:
            # Then try and parse as a date
            try:
                arg = parse_datetimestr_to_std_time(arg)
            except ValueError:
                # Otherwise throw an error
                parser.error("'" + arg + "' is not a valid " + name)
        return arg
    else:
        return None

def parse_as_float_or_time_delta(arg, name, parser):
    from time_util import parse_datetimestr_delta_to_float_days
    if arg:
        try:
            # First try and parse as a float
            arg = float(arg)
        except ValueError:
            # Then try and parse as a timedelta
            try:
                arg = parse_datetimestr_delta_to_float_days(arg)
            except ValueError:
                # Otherwise throw an error
                parser.error("'" + arg + "' is not a valid " + name)
        return arg
    else:
        return None

def check_range(min_val, max_val, step, parser, range_axis):
    '''
    If a val range was specified, checks that they are valid numbers and the min is less than the max
    '''
    ax_range = {}

    if min_val is not None:
        ax_range[range_axis + "min"] = parse_as_float_or_date(min_val, range_axis + "min", parser)

    if max_val is not None:
        ax_range[range_axis + "max"] = parse_as_float_or_date(max_val, range_axis + "max", parser)

    if ax_range.get(range_axis + "min", None) is not None and ax_range.get(range_axis + "max", None) is not None:
        if ax_range[range_axis + "min"] >= ax_range[range_axis + "max"]:
            parser.error(range_axis + "min must be less than " + range_axis + "max")

    if step is not None:
        ax_range[range_axis + "step"] = parse_as_float_or_time_delta(step, range_axis + "step", parser)

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

    arguments.valrange = check_range(arguments.vmin, arguments.vmax, arguments.vstep, parser, "v")
    arguments.xrange = check_range(arguments.xmin, arguments.xmax, arguments.xstep, parser, "x")
    arguments.yrange = check_range(arguments.ymin, arguments.ymax, arguments.ystep, parser, "y")

    arguments.cbarorient = check_colour_bar_orientation(arguments.cbarorient, parser)
    arguments.nocolourbar = check_boolean_argument(arguments.nocolourbar)
    arguments.grid = check_boolean_argument(arguments.grid)

    arguments.coastlinescolour = check_color(arguments.coastlinescolour, parser)

    arguments = assign_logs(arguments)
    # Try and parse numbers
    arguments.itemwidth = parse_float(arguments.itemwidth, "item width", parser)   
    arguments.fontsize = parse_float(arguments.fontsize, "font size", parser)
    arguments.height = parse_float(arguments.height, "height", parser)
    arguments.width = parse_float(arguments.width, "width", parser)
    arguments.xtickangle = parse_float(arguments.xtickangle, "x tick angle", parser)
    arguments.ytickangle = parse_float(arguments.ytickangle, "y tick angle", parser)
    arguments.xbinwidth = parse_float(arguments.xbinwidth, "x bin width", parser)
    arguments.ybinwidth = parse_float(arguments.ybinwidth, "y bin width", parser)
    
    return arguments


def validate_info_args(arguments, parser):
    check_file_exists(arguments.filename, parser)
    return arguments


def validate_col_args(arguments, parser):
    '''
    Checks that the filenames are valid and that variables and methods have been specified.
    Assigns default method/variable to datagroups with unspecified method/variable if default is specified
    Checks that the product is valid if specified
    '''
    # Note: Sample group is put into a list as parse_colonic_arguments expects a list. Samplegroup will only ever be one argument though
    samplegroup = get_col_samplegroup([arguments.samplegroup], parser)

    # Take the three parts out of the 0th samplegroup. Note: Due to the reason stated above, there will only ever be one samplegroup
    arguments.samplefiles = samplegroup[0]["filenames"]
    arguments.samplevariable = samplegroup[0]["variable"] if samplegroup[0]["variable"] is not "" else None
    arguments.sampleproduct = samplegroup[0]["product"]
    arguments.datagroups = get_col_datagroups(arguments.datagroups, parser)

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
        
    return main_args
