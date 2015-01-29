'''
Module used for parsing
'''
import argparse
import re
import sys
import os.path
from jasmin_cis.exceptions import InvalidCommandLineOptionError
from plotting.plot import Plotter
import logging
from utils import add_file_prefix


def initialise_top_parser():
    '''
    The parser to which all arguments are initially passed
    '''
    parser = argparse.ArgumentParser("cis")
    subparsers = parser.add_subparsers(dest='command')
    plot_parser = subparsers.add_parser("plot", help="Create plots")
    add_plot_parser_arguments(plot_parser)
    info_parser = subparsers.add_parser("info", help="Get information about a file")
    add_info_parser_arguments(info_parser)
    col_parser = subparsers.add_parser("col", help="Perform colocation")
    add_col_parser_arguments(col_parser)
    aggregate_parser = subparsers.add_parser("aggregate", help="Perform aggregation")
    add_aggregate_parser_arguments(aggregate_parser)
    subset_parser = subparsers.add_parser("subset", help="Perform subsetting")
    add_subset_parser_arguments(subset_parser)
    eval_parser = subparsers.add_parser("eval", help="Evaluate a numeric expression")
    add_eval_parser_arguments(eval_parser)
    stats_parser = subparsers.add_parser("stats", help="Perform statistical comparison of two datasets")
    add_stats_parser_arguments(stats_parser)
    subparsers.add_parser("version", help="Display the CIS version number")
    return parser


def add_plot_parser_arguments(parser):
    from jasmin_cis.data_io.products.AProduct import AProduct
    import jasmin_cis.plugin as plugin

    product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products', verbose=False)

    parser.add_argument("datagroups", metavar="Input datagroups", nargs="+",
                        help="The datagroups to be plotted, in the format 'variable:filenames[:options]', where "
                             "options are entered in a comma separated list of the form \'keyword=value\'. Available "
                             "options are color, edgecolor, itemstylem, label and product. Colour is any valid html "
                             "colour and product is one of the options listed below. For example 'cis plot "
                             "var1:file:product=NetCDF_CF_Gridded,colour=red'. Products: " +
                             str([cls().__class__.__name__ for cls in product_classes]))
    parser.add_argument("-o", "--output", metavar="Output filename", nargs="?",
                        help="The filename of the output file for the plot image")
    parser.add_argument("--type", metavar="Chart type", nargs="?",
                        help="The chart type, one of: " + str(Plotter.plot_types.keys()))

    parser.add_argument("--xlabel", metavar="X axis label", nargs="?", help="The label for the x axis")
    parser.add_argument("--ylabel", metavar="Y axis label", nargs="?", help="The label for the y axis")
    parser.add_argument("--cbarlabel", metavar="Colour bar label", nargs="?", help="The label for the colour bar")

    parser.add_argument("--xtickangle", metavar="X tick angle", nargs="?",
                        help="The angle (in degrees) of the ticks on the x axis")
    parser.add_argument("--ytickangle", metavar="Y tick angle", nargs="?",
                        help="The angle (in degrees) of the ticks on the y axis")

    parser.add_argument("--title", metavar="Chart title", nargs="?", help="The title for the chart")
    parser.add_argument("--itemwidth", metavar="Item width", nargs="?", help="The width of an item. Unit are points in "
                        "the case of a line, and point^2 in the case of a scatter point.")
    parser.add_argument("--fontsize", metavar="Font size", nargs="?", help="The size of the font in points")
    parser.add_argument("--cmap", metavar="Colour map", nargs="?", help="The colour map used, e.g. RdBu")
    parser.add_argument("--height", metavar="Plot height", nargs="?", help="The height of the plot in inches")
    parser.add_argument("--width", metavar="Plot width", nargs="?", help="The width of the plot in inches")

    parser.add_argument("--xmin", metavar="Minimum x", nargs="?", help="The minimum x value to plot")
    parser.add_argument("--xmax", metavar="Maximum x", nargs="?", help="The maximum x value to plot")
    parser.add_argument("--xstep", metavar="X step", nargs="?", help="The step of the x axis")

    parser.add_argument("--ymin", metavar="Minimum y", nargs="?", help="The minimum y value to plot")
    parser.add_argument("--ymax", metavar="Maximum y", nargs="?", help="The maximum y value to plot")
    parser.add_argument("--ystep", metavar="Y step", nargs="?", help="The step of the y axis")

    parser.add_argument("--vmin", metavar="Minimum value", nargs="?", help="The minimum value to plot")
    parser.add_argument("--vmax", metavar="Maximum value", nargs="?", help="The maximum value to plot")
    parser.add_argument("--vstep", metavar="X value", nargs="?", help="The step of the colour bar")

    parser.add_argument("--xbinwidth", metavar="Histogram x axis bin width", nargs="?",
                        help="The width of the bins on the x axis of a histogram")
    parser.add_argument("--ybinwidth", metavar="Histogram y axis bin width", nargs="?",
                        help="The width of the bins on the y axis of a histogram")

    parser.add_argument("--cbarorient", metavar="Colour bar orientation", default="vertical", nargs="?",
                        help="The orientation of the colour bar, either horizontal or vertical")
    parser.add_argument("--nocolourbar", metavar="Hides the colour bar", default="False", nargs="?",
                        help="Does not show the colour bar")

    parser.add_argument("--logx", metavar="Log (base 10) scale on X axis", default="False", nargs="?",
                        help="Uses a log scale (base 10) on the x axis")
    parser.add_argument("--logy", metavar="Log (base 10) scale on Y axis", default="False", nargs="?",
                        help="Uses a log scale (base 10) on the y axis")
    parser.add_argument("--logv", metavar="Log (base 10) scale for values", default="False", nargs="?",
                        help="Uses a log scale (base 10) on the colour bar")

    parser.add_argument("--grid", metavar="Show grid", default="False", nargs="?", help="Shows grid lines on the plot")
    parser.add_argument("--xaxis", metavar="Variable on x axis", nargs="?",
                        help="Name of variable to use on the x axis")
    parser.add_argument("--yaxis", metavar="Variable on y axis", nargs="?",
                        help="Name of variable to use on the y axis")

    parser.add_argument("--coastlinescolour", metavar="Coastlines Colour", nargs="?",
                        help="The colour of the coastlines on a map. Any valid html colour (e.g. red)")
    parser.add_argument("--nasabluemarble", metavar="NASA Blue Marble background", default=False, nargs="?",
                        help="Add the NASA 'Blue Marble' image as the background to a map, instead of coastlines")

    parser.add_argument("--plotwidth", metavar="Width of the plot in inches", default=8, nargs="?",
                        help="Set the width of the plot when outputting to file")
    parser.add_argument("--plotheight", metavar="Height of the plot in inches", default=6, nargs="?",
                        help="Set the height of the plot when outputting to file")
    parser.add_argument("--cbarscale", metavar="A scaling for the color bar", default=1, nargs="?",
                        help="Scale the color bar, use when color bar does not match plot size")
    return parser


def add_info_parser_arguments(parser):
    parser.add_argument("filename", metavar="Filename", help="The filename of the file to inspect")
    parser.add_argument("-v", "--variables", metavar="Variable(s)", nargs="+", help="The variable(s) to inspect")
    parser.add_argument("--type", metavar="type of HDF data", nargs="?",
                        help="Can be 'VD' or 'SD'. Use 'All' for both.")
    return parser


def add_col_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroups", nargs="+", help="Variables and files to colocate, "
                        "which needs to be entered in the format variables:filename[:product=], with multiple files to "
                        "colocate separated by spaces.")
    parser.add_argument("samplegroup", metavar="SampleGroup", help="A filename with the points to colocate onto. "
                        "Additional parameters are variable, colocator, kernel and product, entered as "
                        "keyword=value. Colocator must always be specified. For example "
                       "filename:variable=var1,colocator=box[h_sep=10km].")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file containing the colocated data. The name specified will"
                             " be suffixed with \".nc\". For ungridded output, it will be prefixed with \"cis-\" and "
                             "so that cis can recognise it when using the file for further operations.")
    return parser


def add_aggregate_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs=1,
                        help="Variables to aggregate with filenames, and optional arguments seperated by colon(s). "
                             "Optional arguments are product and kernel, which are entered as keyword=value in a "
                             "comma separated list. Example: var:filename:product=MODIS_L3,kernel=mean")
    parser.add_argument("aggregategrid", metavar="AggregateGrid",
                        help="Grid for new aggregation, e.g. t,x=[-180,90,5] would collapse time completely and "
                             "aggregate longitude onto a new grid, which would start at -180 and then proceed in 5 "
                             "degree increments up to 90")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file")
    return parser


def add_subset_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs=1,
                        help="Variables to subset with filenames and optional product separated by colon(s)")
    parser.add_argument("subsetranges", metavar="SubsetRanges",
                        help="Dimension ranges to use for subsetting")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file")
    return parser


def add_eval_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs='+',
                        help="Variables to evalute using with filenames and optional product separated by colon(s)")
    parser.add_argument("expr", metavar="Calculation expression to evaluate")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file")


def add_stats_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs='+',
                        help="Variables to perform statistical comparison on and optional product separated by colon(s)")
    parser.add_argument("-o", "--output", metavar="Output filename", nargs="?",
                        help="The filename of the output file (if outputting to file")


def expand_file_list(filenames, parser):
    '''

    :param filenames: A string which is a comma seperated list of filenames, wildcarded filenames or directories
    :param parser: A reference parser for raising errors on
    :return: A flat list of files which exist - with no duplicate
    '''
    from glob import glob
    from jasmin_cis.utils import OrderedSet

    if not filenames:
        parser.error("Please specify at least one filename")
    input_list = filenames.split(',')

    # Ensure we don't get duplicates by making file_set a set
    file_set = OrderedSet()
    for element in input_list:
        if any(wildcard in element for wildcard in ['*', '?', ']', '}']):
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

    :param arg:    The arg to parse as a float
    :param name:   A description of the argument used for error messages
    :param parser: The parser used to report an error message
    :return: The parsed float if succeeds or the original argument if fails
    '''
    if arg:
        try:
            arg = float(arg)
            return arg
        except ValueError:
            parser.error("'" + arg + "' is not a valid " + name)
            return None


def check_float(arg, parser):
    return parse_float(arg, 'unknown', parser)


def parse_int(arg, name, parser):
    '''
    Tries to parse a string as an integer.

    :param arg:    The arg to parse as an integer
    :param name:   A description of the argument used for error messages
    :param parser: The parser used to report an error message
    :return: The parsed integer if succeeds or None if fails
    '''
    if arg:
        try:
            arg = int(arg)
            return arg
        except ValueError:
            parser.error("'" + arg + "' is not a valid " + name)
            return None


def check_int(arg, parser):
    return parse_int(arg, 'unknown', parser)


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


def check_aggregate_kernel(arg, parser):
    import jasmin_cis.plugin as plugin
    from jasmin_cis.col_framework import Kernel
    from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels

    aggregation_classes = plugin.find_plugin_classes(Kernel, 'jasmin_cis.col_implementations')
    aggregation_names = [cls().__class__.__name__ for cls in aggregation_classes]
    if arg in aggregation_kernels.keys() or arg in aggregation_names:
        return arg
    else:
        parser.error(arg + " is not a valid aggregation kernel. Please use one of " + str(aggregation_names))


def get_plot_datagroups(datagroups, parser):
    '''
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "color", "edgecolor", "itemstyle",
                                                       "label", "product", "type", "transparency", "cmap", "cmin",
                                                       "cmax", "contnlevels", "contlevels", "contlabel", "contwidth",
                                                       "contfontsize"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, check_color, check_color, check_nothing,
                                         check_nothing, check_product, check_plot_type, check_float, check_nothing,
                                         check_float, check_float, check_int, convert_to_list_of_floats, check_boolean,
                                         check_float, check_float)
    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsary_args=2)


def get_col_samplegroup(samplegroup, parser):
    '''
    :param samplegroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed samplegroups as a list of dictionaries
    '''
    from collections import namedtuple

    DatagroupOptions = namedtuple('SamplegroupOptions',
                                  ["filenames", "variable", "colocator", "constraint", "kernel", "product"])
    samplegroup_options = DatagroupOptions(expand_file_list, check_nothing, extract_method_and_args,
                                           extract_method_and_args, extract_method_and_args, check_product)

    return parse_colon_and_comma_separated_arguments(samplegroup, parser, samplegroup_options, compulsary_args=1)[0]


def get_aggregate_datagroups(datagroups, parser):
    '''
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product", "kernel"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product,
                                         check_aggregate_kernel)

    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsary_args=2)


def get_eval_datagroups(datagroups, parser):
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product)

    datagroups = parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsary_args=2)

    # Evaluate allows aliases in variable names so we need to process them here.
    _set_aliases_for_datagroups(datagroups, parser)
    return datagroups


def get_aggregate_grid(aggregategrid, parser):
    '''
    :param aggregategrid: List of aggregate grid specifications 
    :param parser:        The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    '''
    from jasmin_cis.parse_datetime import parse_datetime, parse_datetime_delta, parse_as_number_or_datetime
    from jasmin_cis.aggregation.aggregation_grid import AggregationGrid

    # Split into the limits for each dimension.
    split_input = split_outside_brackets(aggregategrid)
    if len(split_input) == 0:
        parser.error("Limits for at least one dimension must be specified for aggregation")

    grid_dict = {}
    for seg in split_input:
        # Parse out dimension name and new grid spacing; the expected format is:
        # <dim_name>=[<start_value>,<end_value,<delta>]
        match = re.match(r'(?P<dim>[^=]+)(?:=)?(?:\[(?P<start>[^],]+)?(?:,(?P<end>[^],]+))?(?:,(?P<delta>[^]]+))?\])?',
                         seg)
        if match is None or match.group('dim') is None:
            parser.error("A dimension for aggregation does not have a valid dimension name")
        elif match.group('start') is None and match.group('delta') is None:
            dim_name = match.group('dim')
            grid_dict[dim_name] = AggregationGrid(float('NaN'), float('NaN'), float('NaN'), None)
        elif match.group('end') is None:
            parser.error("A dimension for aggregation has a start point but no end or delta value, an end and a delta "
                         "value must be supplied, for example x=[0,360,30].")
        elif match.group('delta') is None:
            parser.error("A dimension for aggregation has a start point but no delta value, a delta value must be "
                         "supplied, for example x=[0,360,30].")
        else:
            dim_name = match.group('dim')
            start = match.group('start')
            end = match.group('end')
            delta = match.group('delta')

            # If the dimension is specified as x, y, z, p or t, assume that the dimension is spatial or temporal in the
            # obvious way. Otherwise, parse what is found as a date/time or number.
            is_time = None
            if dim_name.lower() == 't':
                start_parsed = parse_datetime(start, 'aggregation grid start date/time', parser)
                end_parsed = parse_datetime(end, 'aggregation grid end date/time', parser)
                delta_parsed = parse_datetime_delta(delta, 'aggregation grid delta date/time', parser)
                is_time = True
            elif dim_name.lower() in ['x', 'y', 'z', 'p']:
                start_parsed = parse_float(start, 'aggregation grid start coordinate', parser)
                end_parsed = parse_float(end, 'aggregation grid end coordinate', parser)
                delta_parsed = parse_float(delta, 'aggregation grid delta coordinate', parser)
                is_time = False
            else:
                start_parsed = parse_as_number_or_datetime(start, 'aggregation grid start coordinate', parser)
                end_parsed = parse_as_number_or_datetime(end, 'aggregation grid end coordinate', parser)
                delta_parsed = parse_as_number_or_datetime(delta, 'aggregation grid delta coordinate', parser)
            grid_dict[dim_name] = AggregationGrid(start_parsed, end_parsed, delta_parsed, is_time)

    return grid_dict


def get_basic_datagroups(datagroups, parser):
    '''
    Get datagroups containing only variables:filenames:product
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    '''
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product)

    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsary_args=2)


def get_subset_limits(subsetlimits, parser):
    '''
    :param subsetlimits:  List of subset limit strings
    :param parser:        The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    '''
    from jasmin_cis.parse_datetime import parse_datetime, parse_as_number_or_datetime
    from jasmin_cis.subsetting.subset_limits import SubsetLimits

    # Split into the limits for each dimension.
    split_input = split_outside_brackets(subsetlimits)
    if len(split_input) == 0:
        parser.error("Limits for at least one dimension must be specified for subsetting")

    limit_dict = {}
    for seg in split_input:
        # Parse out dimension name and limit value strings; the expected format is:
        # <dim_name>=[<start_value>,<end_value>]
        # or
        # <dim_name>=[<start_value>]
        match = re.match(r'(?P<dim>[^=]+)=\[(?P<start>[^],]+)(?:,(?P<end>[^],]+))?\]$', seg)
        if match is None or match.group('dim') is None or match.group('start') is None:
            parser.error(
                "A dimension for subsetting does not have dimension name, start value and/or end value specified")
        else:
            dim_name = match.group('dim')
            limit1 = match.group('start')
            if match.group('end') is None:
                limit2 = limit1
            else:
                limit2 = match.group('end')

            # If the dimension is specified as x, y, z, or t, assume that the dimension is spatial or temporal in the
            # obvious way. Otherwise, parse what is found as a date/time or number.
            is_time = None
            if dim_name.lower() == 't':
                limit1_parsed = parse_datetime(limit1, 'subset range start date/time', parser)
                limit2_parsed = parse_datetime(limit2, 'subset range end date/time', parser)
                is_time = True
            elif dim_name.lower() in ['x', 'y', 'z']:
                limit1_parsed = parse_float(limit1, 'subset range start coordinate', parser)
                limit2_parsed = parse_float(limit2, 'subset range start coordinate', parser)
                is_time = False
            else:
                limit1_parsed = parse_as_number_or_datetime(limit1, 'subset range start coordinate', parser)
                limit2_parsed = parse_as_number_or_datetime(limit2, 'subset range start coordinate', parser)
            limit_dict[dim_name] = SubsetLimits(limit1_parsed, limit2_parsed, is_time)
    return limit_dict


def parse_colonic_arguments(inputs, parser, options, min_args=1):
    '''
    :param inputs:    A list of strings, each in the format a:b:c:......:n where a,b,c,...,n are arguments
    :param parser:    The parser used to raise an error if one occurs
    :param options:   The possible options that each input can take. If no value is assigned to a particular option, then it is assigned None
    :param min_args:   The minimum number of arguments to expect - we can't say which arguments are compulsory, just how many are
    :return: A list of dictionaries containing the parsed arguments
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


def parse_colon_and_comma_separated_arguments(inputs, parser, options, compulsary_args):
    '''
    :param inputs:    A list of strings, each in the format a:b:c:......:n where a,b,c,...,n are arguments
    :param parser:    The parser used to raise an error if one occurs
    :param options:   The possible options that each input can take. If no value is assigned to a particular option, then it is assigned None
    :param compulsary_args:   The exact number of compulsary arguments (colon separated)
    :return: A list of dictionaries containing the parsed arguments
    '''
    input_dicts = []

    for input_string in inputs:
        split_input = input_string.split(":")
        if len(split_input) < compulsary_args:
            parser.error("A mandatory option is missing")
        elif len(split_input) > compulsary_args + 1:
            parser.error("Too many mandatory options")

        input_dict = {}

        option = options._asdict().keys()

        # First deal with the comma separated compulsary arguments
        for i in range(0, compulsary_args):
            try:
                current_option = split_input[i]
                input_dict[option[0]] = options[i](current_option, parser)
                option.pop(0)  # Compulsary arguments always the first in the list
            except IndexError:
                input_dict[option[i]] = None

        # Now deal with optional arugments, if they exist. For each option loop through the list of arguments to see if
        # it exists, if so check and add to the dictionary.
        if len(split_input) == compulsary_args + 1:
            split_input_comma = split_outside_brackets(split_input[-1])
        else:
            split_input_comma = []  # need to loop over options to set optional arguments to None

        if len(split_input_comma) > len(option):
            raise InvalidCommandLineOptionError('More options specified than are actually available.')

        # If there is only one optional argument do not require the 'keyword=' syntax
        if len(option) == 1 and len(split_input_comma) == 1:
            split_input_variable = split_outside_brackets(split_input_comma[0], '=')
            if len(split_input_variable) == 1:
                input_dict[option[0]] = split_input_variable[0]
                option.pop(0)
                split_input_comma.pop(0)
            elif len(split_input_variable) == 2:
                if option[0] == split_input_variable[0]:
                    input_dict[option[0]] = split_input_variable[1]
                    option.pop(0)
                    split_input_comma.pop(0)
            else:
                raise InvalidCommandLineOptionError('Something is wrong with this argument: ', split_input_comma)

        for i, option in enumerate(option):
            # Make sure an entry for each option is created, even if it is None
            input_dict[option] = None
            for j in split_input_comma:
                # Split the input, [0] will be the key and [1] the value in the list
                split_input_variable = split_outside_brackets(j, '=')
                if split_input_variable[0] == option:
                    input_dict[option] = options[i + compulsary_args](split_input_variable[1], parser)
                    split_input_comma.remove(j)

        if len(split_input_comma) != 0:
            raise InvalidCommandLineOptionError('The following optional arguments could not be parsed: ' +
                                                str(split_input_comma))

        input_dicts.append(input_dict)
    return input_dicts


def split_outside_brackets(input, seps=[','], brackets={'[': ']'}):
    """Splits an input string at separators that are not within brackets.
    :param input: input string to parse
    :param seps: list of separator characters - default: comma
    :param brackets: map of open brackets to corresponding close brackets: default: square brackets
    :return: list of strings formed by breaking the input at colons
    """
    match_brackets = []
    match_bracket = None
    in_brackets = 0
    sep_idxs = []
    for idx in range(0, len(input)):
        if input[idx] in brackets:
            if in_brackets > 0:
                match_brackets.append(match_bracket)
            match_bracket = brackets[input[idx]]
            in_brackets += 1
        elif in_brackets > 0 and input[idx] == match_bracket:
            in_brackets -= 1
            if in_brackets > 0:
                match_bracket = match_brackets.pop()
        elif input[idx] in seps and in_brackets == 0:
            sep_idxs.append(idx)

    output = []
    start_idx = 0
    for idx in sep_idxs:
        output.append(input[start_idx:idx])
        start_idx = idx + 1
    if start_idx < len(input):
        output.append(input[start_idx:])
    return output


def extract_method_and_args(arguments, parser):
    from jasmin_cis.utils import parse_key_val_list

    if not arguments:
        method_and_args = None
    else:
        elements = multi_split(arguments, ['[', ',', ']'])
        method_name = elements[0]
        args = elements[1:] if len(elements) > 1 else []
        method_and_args = ( method_name, parse_key_val_list(args) )
    return method_and_args


def multi_split(s, seps):
    """Does a string split for multiple separators, and removes any blanks
    :param s: input string to parse
    :param seps: separators to use - the order of these matter
    """
    res = [s]
    for sep in seps:
        # For each separator perform the split, and append to res
        s, res = res, []
        for seq in s:
            res += seq.split(sep)

    for i in res:
        # Remove empty strings
        if not i:
            res.pop(res.index(i))

    return res


def check_nothing(item, parser):
    return item


def check_is_not_empty(item, parser):
    if not item:
        parser.error("Non optional argument not specified in datagroup")
    return item


def check_is_not_empty_and_comma_split(item, parser):
    check_is_not_empty(item, parser)
    return multi_split(item, [','])


def _set_aliases_for_datagroups(datagroups, parser):
    """
    Split out aliases from variables in a datagroup. They will be of the form:
    'var1=alias1' where the part after the '=' is the alias.
    :param datagroup: Arguments.datagroup
    :return:
    """

    def _alias_error(var_and_alias):
        parser.error("Invalid variable name or aliasing: expected string of form '<variablename>=<alias>', "
                     "but got: '%s'" % var_and_alias)
    all_aliases = []
    for datagroup in datagroups:
        variables = []
        aliases = []
        for variable in datagroup['variables']:
            parts = variable.split('=')
            if len(parts) == 1:
                if not parts[0]:
                    _alias_error(variable)
                variables.append(variable)
                aliases.append(variable)
            elif len(parts) == 2:
                if not (parts[0] and parts[1]):
                    _alias_error(variable)
                variables.append(parts[0])
                aliases.append(parts[1])
            elif len(parts) > 2:
                _alias_error(variable)
        datagroup['aliases'] = aliases
        all_aliases.extend(aliases)
        datagroup['variables'] = variables
    # Check that the set of aliases is all unique
    if not len(set(all_aliases)) == len(all_aliases):
        parser.error("Variable names or aliases must be all unique: list was %s" % all_aliases)


def convert_to_list_of_floats(arg, parser):
    # Given a string such as '[10.0,11.1,12.2]' retruns a list containing, 10.0, 11.1, 12.2
    return [float(x) for x in arg[1:-1].split(',')]


def check_plot_type(plot_type, parser):
    '''
    Checks plot type is valid option for number of variables if specified
    '''

    if plot_type is not None:
        if plot_type not in Plotter.plot_types.keys():
            parser.error(
                "'" + plot_type + "' is not a valid plot type, please use one of: " + str(Plotter.plot_types.keys()))

    return plot_type


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


def check_valid_min_max_args(min_val, max_val, step, parser, range_axis):
    '''
    If a val range was specified, checks that they are valid numbers and the min is less than the max
    '''
    from jasmin_cis.parse_datetime import parse_as_number_or_datetime
    from jasmin_cis.time_util import parse_datetimestr_to_std_time
    import datetime

    ax_range = {}

    if min_val is not None:
        dt = parse_as_number_or_datetime(min_val, range_axis + "min", parser)
        if isinstance(dt, datetime.datetime):
            ax_range[range_axis + "min"] = parse_datetimestr_to_std_time(str(datetime.datetime(*dt)))
        else:
            ax_range[range_axis + "min"] = dt

    if max_val is not None:
        dt = parse_as_number_or_datetime(max_val, range_axis + "max", parser)
        if isinstance(dt, datetime.datetime):
            ax_range[range_axis + "max"] = parse_datetimestr_to_std_time(str(datetime.datetime(*dt)))
        else:
            ax_range[range_axis + "max"] = dt

    if step is not None:
        ax_range[range_axis + "step"] = parse_as_float_or_time_delta(step, range_axis + "step", parser)

    return ax_range


def check_boolean_argument(argument):
    if argument is None or argument != "False":
        return True
    else:
        return False


def check_boolean(arg, parser):
    if arg is None or arg.lower() == "true":
        return True
    elif arg.lower() == "false":
        return False
    else:
        parser.error("'" + arg + "' is not either True or False")


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


def _split_output_if_includes_variable_name(arguments, parser):
    arguments.output_var = None
    if ':' in arguments.output:
        try:
            arguments.output_var, arguments.output = arguments.output.split(':')
        except ValueError:
            # Too many values to unpack
            parser.error("Invalid output path: should be a filename with one optional variable prefix.")


def _validate_output_file(arguments, parser):
    _split_output_if_includes_variable_name(arguments, parser)
    _check_output_filepath_not_input(arguments, parser)
    _append_file_extension_to_output_if_missing(arguments, parser, '.nc')


def _append_file_extension_to_output_if_missing(arguments, parser, extension):
    if not extension:
        parser.error("Invalid file extension: '%s'" % extension)
    if not extension.startswith('.'):
        extension = '.' + extension
    if not arguments.output.endswith(extension):
        arguments.output = arguments.output + extension


def _check_output_filepath_not_input(arguments, parser):
    try:
        input_files = list(arguments.samplefiles)
    except AttributeError:
        input_files = []  # Only applies to colocation

    for datagroup in arguments.datagroups:
        input_files.extend(datagroup['filenames'])
    gridded_output_file = arguments.output + ".nc"
    ungridded_output_file = add_file_prefix('cis-', gridded_output_file)
    for output_file in [gridded_output_file, ungridded_output_file]:
        for input_file in input_files:
            if os.path.exists(output_file):
                if os.path.samefile(output_file, input_file):
                    parser.error("The input file must not be the same as the output file")


def validate_plot_args(arguments, parser):
    arguments.datagroups = get_plot_datagroups(arguments.datagroups, parser)
    check_plot_type(arguments.type, parser)

    arguments.valrange = check_valid_min_max_args(arguments.vmin, arguments.vmax, arguments.vstep, parser, "v")
    arguments.xrange = check_valid_min_max_args(arguments.xmin, arguments.xmax, arguments.xstep, parser, "x")
    arguments.yrange = check_valid_min_max_args(arguments.ymin, arguments.ymax, arguments.ystep, parser, "y")

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
    arguments.samplegroup = get_col_samplegroup([arguments.samplegroup], parser)

    # Take the three parts out of the 0th samplegroup. Note: Due to the reason stated above, there will only ever be one samplegroup
    arguments.samplefiles = arguments.samplegroup["filenames"]
    arguments.samplevariable = arguments.samplegroup["variable"] if arguments.samplegroup[
                                                                        "variable"] is not "" else None
    arguments.sampleproduct = arguments.samplegroup["product"]
    if arguments.samplegroup["colocator"] is None:
        parser.error("You must specify a colocator")
    arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    _validate_output_file(arguments, parser)

    return arguments


def validate_aggregate_args(arguments, parser):
    arguments.datagroups = get_aggregate_datagroups(arguments.datagroups, parser)
    arguments.grid = get_aggregate_grid(arguments.aggregategrid, parser)
    _validate_output_file(arguments, parser)
    return arguments


def validate_subset_args(arguments, parser):
    arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    arguments.limits = get_subset_limits(arguments.subsetranges, parser)
    _validate_output_file(arguments, parser)
    return arguments


def validate_eval_args(arguments, parser):
    arguments.datagroups = get_eval_datagroups(arguments.datagroups, parser)
    _validate_output_file(arguments, parser)
    return arguments


def validate_stats_args(arguments, parser):
    arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    num_vars = 0
    for datagroup in arguments.datagroups:
        num_vars += len(datagroup['variables'])
    if num_vars != 2:
        parser.error("Stats command requires exactly two variables (%s were given)" % num_vars)
    if arguments.output:
        _validate_output_file(arguments, parser)
    return arguments


def validate_version_args(arguments, parser):
    # no arguments accepted
    return arguments


validators = {'plot': validate_plot_args,
              'info': validate_info_args,
              'col': validate_col_args,
              'aggregate': validate_aggregate_args,
              'subset': validate_subset_args,
              'eval': validate_eval_args,
              'stats': validate_stats_args,
              'version': validate_version_args}


def parse_args(arguments=None):
    '''
    Parse the arguments given. If no arguments are given, then used the command line arguments.
    Returns a dictionary contains the parsed arguments
    '''
    parser = initialise_top_parser()
    if arguments is None:
        # sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args = parser.parse_args(arguments)
    main_args = validators[main_args.command](main_args, parser)

    return main_args
