"""
Module used for parsing
"""
import argparse
import re
import sys
import os.path
import logging

from cis.exceptions import InvalidCommandLineOptionError
from cis.plotting.plot import plot_types, projections


class AliasedSubParsersAction(argparse._SubParsersAction):
    """
    Manually add aliases (which aren't supported in Python 2...
    From https://gist.github.com/sampsyo/471779
    """

    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ','.join(aliases)
            super(AliasedSubParsersAction._AliasedPseudoAction, self).__init__(option_strings=[], dest=dest, help=help)

    def add_parser(self, name, **kwargs):
        if 'aliases' in kwargs:
            aliases = kwargs['aliases']
            del kwargs['aliases']
        else:
            aliases = []

        parser = super(AliasedSubParsersAction, self).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser
        # Make the help text reflect them, first removing old help entry.
        if 'help' in kwargs:
            help = kwargs.pop('help')
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser


def initialise_top_parser():
    """
    The parser to which all arguments are initially passed
    """
    global_options = argparse.ArgumentParser(add_help=False)
    verbosity_group = global_options.add_mutually_exclusive_group()
    verbosity_group.add_argument("-v", "--verbose", action='count',
                                 help="Increase the level of logging information output to screen to include "
                                      "'Info' statements")
    verbosity_group.add_argument("-q", "--quiet", action='store_true',
                                 help="Suppress all output to the screen, only 'Error' messages will be displayed "
                                      "(which are always fatal).")
    global_options.add_argument("--force-overwrite", action='store_true',
                                help="Do not prompt when an output file already exists - always overwrite. This can "
                                     "also be set by setting the 'CIS_FORCE_OVERWRITE' environment variable to 'TRUE'")

    parser = argparse.ArgumentParser("cis", parents=[global_options])
    parser.register('action', 'parsers', AliasedSubParsersAction)
    subparsers = parser.add_subparsers(dest='command')
    plot_parser = subparsers.add_parser("plot", help="Create plots", argument_default=argparse.SUPPRESS, parents=[global_options])
    add_plot_parser_arguments(plot_parser)
    info_parser = subparsers.add_parser("info", help="Get information about a file", parents=[global_options])
    add_info_parser_arguments(info_parser)
    col_parser = subparsers.add_parser("collocate", aliases=['col'], help="Perform collocation", parents=[global_options])
    add_col_parser_arguments(col_parser)
    aggregate_parser = subparsers.add_parser("aggregate", aliases=['agg'], help="Perform aggregation", parents=[global_options])
    add_aggregate_parser_arguments(aggregate_parser)
    subset_parser = subparsers.add_parser("subset", aliases=['sub'], help="Perform subsetting", parents=[global_options])
    add_subset_parser_arguments(subset_parser)
    eval_parser = subparsers.add_parser("eval", help="Evaluate a numeric expression", parents=[global_options])
    add_eval_parser_arguments(eval_parser)
    stats_parser = subparsers.add_parser("stats", help="Perform statistical comparison of two datasets",
                                         parents=[global_options])
    add_stats_parser_arguments(stats_parser)
    collapse_parser = subparsers.add_parser("collapse", help="Collapse a gridded dataset over specified dimensions",
                                            parents=[global_options])
    add_collapse_parser_arguments(collapse_parser)
    subparsers.add_parser("version", help="Display the CIS version number")
    return parser


def add_plot_parser_arguments(parser):
    from cis.data_io.products.AProduct import AProduct
    from cis.parse_datetime import parse_as_number_or_datetime_delta, parse_as_number_or_datetime
    import cis.plugin as plugin
    from matplotlib.colors import cnames

    product_classes = plugin.find_plugin_classes(AProduct, 'cis.data_io.products', verbose=False)

    parser.add_argument("datagroups", metavar="Input datagroups", nargs="+",
                        help="The datagroups to be plotted, in the format 'variable:filenames[:options]', where "
                             "options are entered in a comma separated list of the form \'keyword=value\'. Available "
                             "options are color, edgecolor, itemstylem, label and product. Colour is any valid html "
                             "colour and product is one of the options listed below. For example 'cis plot "
                             "var1:file:product=NetCDF_CF_Gridded,colour=red'. Products: " +
                             str([cls().__class__.__name__ for cls in product_classes]))
    parser.add_argument("-o", "--output", metavar="Output filename", nargs="?", default=None,
                        help="The filename of the output file for the plot image")
    parser.add_argument("--type", metavar="Chart type", nargs="?",
                        help="The chart type, one of: " + str(plot_types.keys()),
                        choices=plot_types.keys())

    parser.add_argument("--xlabel", metavar="X axis label", nargs="?", help="The label for the x axis")
    parser.add_argument("--ylabel", metavar="Y axis label", nargs="?", help="The label for the y axis")
    parser.add_argument("--cbarlabel", metavar="Colour bar label", nargs="?", help="The label for the colour bar")

    parser.add_argument("--title", metavar="Chart title", nargs="?", help="The title for the chart")
    parser.add_argument("--fontsize", metavar="Font size", nargs="?", help="The size of the font in points", type=float)
    parser.add_argument("--cmap", metavar="Colour map", nargs="?", help="The colour map used, e.g. RdBu")
    parser.add_argument("--height", metavar="Plot height", nargs="?", help="The height of the plot in inches",
                        type=float)
    parser.add_argument("--width", metavar="Plot width", nargs="?", help="The width of the plot in inches", type=float)

    parser.add_argument("--xmin", metavar="Minimum x", nargs="?", help="The minimum x value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--xmax", metavar="Maximum x", nargs="?", help="The maximum x value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--xstep", metavar="X step", nargs="?", help="The step of the x axis",
                        type=parse_as_number_or_datetime_delta)

    parser.add_argument("--ymin", metavar="Minimum y", nargs="?", help="The minimum y value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--ymax", metavar="Maximum y", nargs="?", help="The maximum y value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--ystep", metavar="Y step", nargs="?", help="The step of the y axis",
                        type=parse_as_number_or_datetime_delta)

    parser.add_argument("--vmin", metavar="Minimum value", nargs="?", help="The minimum value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--vmax", metavar="Maximum value", nargs="?", help="The maximum value to plot",
                        type=parse_as_number_or_datetime)
    parser.add_argument("--vstep", metavar="X value", nargs="?", help="The step of the colour bar",
                        type=parse_as_number_or_datetime_delta)

    parser.add_argument("--xbins", metavar="Number of histogram x axis bins", nargs="?",
                        help="The number of bins on the x axis of a histogram", type=int)
    parser.add_argument("--ybins", metavar="Number of histogram x axis bins", nargs="?",
                        help="The number of bins on the y axis of a histogram", type=int)

    parser.add_argument("--cbarorient", metavar="Colour bar orientation", nargs="?",
                        help="The orientation of the colour bar, either horizontal or vertical",
                        choices=['vertical', 'horizontal'])
    parser.add_argument("--nocolourbar", dest='colourbar',
                        help="Does not show the colour bar", action='store_false')

    parser.add_argument("--logx",
                        help="Uses a log scale (base 10) on the x axis", action='store_true')
    parser.add_argument("--logy",
                        help="Uses a log scale (base 10) on the y axis", action='store_true')
    parser.add_argument("--logv",
                        help="Uses a log scale (base 10) on the colour bar", action='store_true')

    parser.add_argument("--grid", help="Shows grid lines on the plot",
                        action='store_true')

    parser.add_argument("--xaxis", metavar="Variable on x axis", nargs="?",
                        help="Name of variable to use on the x axis")
    parser.add_argument("--yaxis", metavar="Variable on y axis", nargs="?",
                        help="Name of variable to use on the y axis")

    parser.add_argument("--coastlinescolour", metavar="Coastlines Colour", nargs="?",
                        help="The colour of the coastlines on a map. Any valid html colour (e.g. red)",
                        choices=(list(cnames.keys()) + ['grey']))
    parser.add_argument("--nasabluemarble",
                        help="Add the NASA 'Blue Marble' image as the background to a map, instead of coastlines",
                        action='store_true')

    parser.add_argument("--cbarscale", metavar="A scaling for the color bar", nargs="?",
                        help="Scale the color bar, use when color bar does not match plot size", type=float)

    parser.add_argument("--projection", choices=projections.keys())

    # Taylor diagram specific options
    parser.add_argument('--solid', action='store_true', help='Use solid markers')
    parser.add_argument('--extend', type=float, help='Extend plot for negative correlation')
    parser.add_argument('--fold', action='store_true', help='Fold plot for negative correlation or large variance')
    parser.add_argument('--gammamax', type=float, help='Fix maximum extent of radial axis')
    parser.add_argument('--stdbiasmax', type=float, help='Fix maximum standardised bias')
    parser.add_argument('--bias', metavar='METHOD', choices=['color', 'colour', 'size', 'flag'],
                        help='Indicate bias using the specified method (colo[u]r, size, flag)')

    return parser


def add_info_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroups", nargs=1,
                        help="Variables and files to inspect, which needs to be entered in the format "
                             "[variables:]filename[:product=].")
    parser.add_argument("--type", metavar="Type of HDF data", nargs="?",
                        help="Can be 'VD' or 'SD'. Use 'All' for both.")
    return parser


def add_col_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroups", nargs="+",
                        help="Variables and files to collocate, which needs to be entered in the format "
                             "variables:filename[:product=], with multiple files to collocate separated by spaces.")
    parser.add_argument("samplegroup", metavar="SampleGroup",
                        help="A filename with the points to collocate onto. Additional parameters are variable, "
                             "collocator, kernel and product, entered as keyword=value. Collocator must always be "
                             "specified. For example filename:variable=var1,collocator=box[h_sep=10km].")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file containing the collocated data. The name specified will"
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


def add_collapse_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs=1,
                        help="Variables to aggregate with filenames, and optional arguments seperated by colon(s). "
                             "Optional arguments are product and kernel, which are entered as keyword=value in a "
                             "comma separated list. Example: var:filename:product=MODIS_L3,kernel=mean")
    parser.add_argument('dimensions', metavar='dim', type=str, nargs='+',
                        help='Dimensions to collapse')
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
    parser.add_argument("units", metavar="Units of output expression")
    parser.add_argument("-o", "--output", metavar="Output filename", default="out", nargs="?",
                        help="The filename of the output file")
    parser.add_argument("-a", "--attributes", metavar="Output metadata attributes", nargs="?")


def add_stats_parser_arguments(parser):
    parser.add_argument("datagroups", metavar="DataGroup", nargs='+',
                        help="Variables to perform statistical comparison on and optional product separated by "
                             "colon(s)")
    parser.add_argument("-o", "--output", metavar="Output filename", nargs="?",
                        help="The filename of the output file (if outputting to file")


def expand_file_list(filenames, parser):
    """

    :param filenames: A string which is a comma seperated list of filenames, wildcarded filenames or directories
    :param parser: A reference parser for raising errors on
    :return: A flat list of files which exist - with no duplicate
    """
    from cis.data_io.data_reader import expand_filelist

    if not filenames:
        parser.error("Please specify at least one filename")

    try:
        file_set = expand_filelist(filenames)
    except ValueError as e:
        parser.error(str(e))

    # Check we matched at least one file
    if file_set:
        logging.info("Identified input file list: " + str(file_set))
    else:
        parser.error("No files found which match: " + str(filenames))

    return file_set


def check_file_exists(filename, parser):
    if not os.path.isfile(filename):
        parser.error("'" + filename + "' is not a valid filename")


def parse_float(arg, name, parser):
    """
    Tries to parse a string as a float.

    :param arg:    The arg to parse as a float
    :param name:   A description of the argument used for error messages
    :param parser: The parser used to report an error message
    :return: The parsed float if succeeds or the original argument if fails
    """
    if arg == 'None' or arg is None:
        return None
    else:
        try:
            arg = float(arg)
            return arg
        except ValueError:
            parser.error("'" + arg + "' is not a valid " + name)
            return None


def check_float(arg, parser):
    return parse_float(arg, 'unknown', parser)


def parse_int(arg, name, parser):
    """
    Tries to parse a string as an integer.

    :param arg:    The arg to parse as an integer
    :param name:   A description of the argument used for error messages
    :param parser: The parser used to report an error message
    :return: The parsed integer if succeeds or None if fails
    """
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
    from cis.data_io.products.AProduct import AProduct
    import cis.plugin as plugin

    if product:
        product_classes = plugin.find_plugin_classes(AProduct, 'cis.data_io.products.products')
        product_names = [cls().__class__.__name__ for cls in product_classes]
        if product not in product_names:
            parser.error(product + " is not a valid product. Please use one of " + str(product_names))
    else:
        product = None
    return product


def check_aggregate_kernel(arg, parser):
    import cis.plugin as plugin
    from cis.collocation.col_framework import Kernel
    from cis.aggregation.collapse_kernels import aggregation_kernels

    aggregation_classes = plugin.find_plugin_classes(Kernel, 'cis.collocation.col_implementations')
    aggregation_names = [cls().__class__.__name__ for cls in aggregation_classes]
    if arg in list(aggregation_kernels.keys()) or arg in aggregation_names:
        return arg
    else:
        parser.error(arg + " is not a valid aggregation kernel. Please use one of " + str(aggregation_names))


def get_plot_datagroups(datagroups, parser):
    """
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    """
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "color", "edgecolor", "itemstyle",
                                                       "itemwidth",
                                                       "label", "product", "type", "alpha", "cmap", "vmin",
                                                       "vmax", "vstep", "contnlevels", "contlevels", "contlabel", "contwidth",
                                                       "cbarscale", "cbarorient", "colourbar", "cbarlabel"])
    datagroup_options = DatagroupOptions(check_is_not_empty, expand_file_list, check_color, check_color, check_nothing,
                                         check_float,
                                         check_nothing, check_product, check_plot_type, check_float, check_nothing, check_float,
                                         check_float, check_float, check_int, convert_to_list_of_floats, check_boolean, check_int,
                                         check_float, check_nothing, check_boolean, check_nothing)
    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsory_args=2)


def get_col_samplegroup(samplegroup, parser):
    """
    :param samplegroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed samplegroups as a list of dictionaries
    """
    from collections import namedtuple

    DatagroupOptions = namedtuple('SamplegroupOptions',
                                  ["filenames", "variable", "collocator", "constraint", "kernel", "product"])
    samplegroup_options = DatagroupOptions(expand_file_list, check_nothing, extract_method_and_args,
                                           extract_method_and_args, extract_method_and_args, check_product)

    return parse_colon_and_comma_separated_arguments(samplegroup, parser, samplegroup_options, compulsory_args=1)[0]


def get_aggregate_datagroups(datagroups, parser):
    """
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    """
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product", "kernel"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product,
                                         check_aggregate_kernel)

    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsory_args=2)


def get_eval_datagroups(datagroups, parser):
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product)

    datagroups = parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsory_args=2)

    # Evaluate allows aliases in variable names so we need to process them here.
    _set_aliases_for_datagroups(datagroups, parser)
    return datagroups


def get_aggregate_grid(aggregategrid, parser):
    """
    :param aggregategrid: List of aggregate grid specifications
    :param parser:        The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    """
    from cis.parse_datetime import parse_as_number_or_datetime, parse_as_number_or_datetime_delta

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
            # This is for gridded aggregation where we just have a list of dims with no grid
            grid_dict[match.group('dim')] = None
        elif match.group('end') is None:
            parser.error("A dimension for aggregation has a start point but no end or delta value, an end and a delta "
                         "value must be supplied, for example x=[0,360,30].")
        elif match.group('delta') is None:
            parser.error("A dimension for aggregation has a start point but no delta value, a delta value must be "
                         "supplied, for example x=[0,360,30].")
        else:
            dim_name = match.group('dim')

            start_parsed = parse_as_number_or_datetime(match.group('start'))
            end_parsed = parse_as_number_or_datetime(match.group('end'))
            delta_parsed = parse_as_number_or_datetime_delta(match.group('delta'))

            if dim_name.lower() == 'x':
                if not start_parsed <= end_parsed:
                    parser.error("Longitude grid must be monotonically increasing (i.e. for x[A,B,C] A <= B). For "
                                 "example, x=[90,-90,10] is invalid but x=[90,270,10] is valid")
                if not end_parsed - start_parsed <= 360:
                    parser.error("Longitude grid should not be wider than 360 degrees "
                                 "(i.e. for x[A,B,C] B-A <= 360)")

            grid_dict[dim_name] = slice(start_parsed, end_parsed, delta_parsed)

    return grid_dict


def get_basic_datagroups(datagroups, parser):
    """
    Get datagroups containing only variables:filenames:product
    :param datagroups:    A list of datagroups (possibly containing colons)
    :param parser:       The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    """
    from collections import namedtuple

    DatagroupOptions = namedtuple('DatagroupOptions', ["variables", "filenames", "product"])
    datagroup_options = DatagroupOptions(check_is_not_empty_and_comma_split, expand_file_list, check_product)

    return parse_colon_and_comma_separated_arguments(datagroups, parser, datagroup_options, compulsory_args=2)


def get_subset_limits(subsetlimits, parser):
    """
    :param subsetlimits:  List of subset limit strings
    :param parser:        The parser used to report errors
    :return: The parsed datagroups as a list of dictionaries
    """
    from cis.parse_datetime import parse_datetime, parse_as_number_or_datetime, parse_partial_datetime

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
        if seg.startswith('shape'):
            # Don't use the regexp for this as it gets confused with the commas
            limit_dict['shape'] = seg.split('=')[1]
        elif match is None or match.group('dim') is None or match.group('start') is None:
            parser.error(
                "A dimension for subsetting does not have dimension name, start value and/or end value specified")
        else:
            dim_name = match.group('dim')
            limit_dict[dim_name] = []

            limit1 = match.group('start')
            limit2 = match.group('end')

            # If the dimension is specified as x, y, z, or t, assume that the dimension is spatial or temporal in the
            # obvious way. Otherwise, parse what is found as a date/time or number.
            if dim_name.lower() == 't' or dim_name.lower() == 'time':
                if limit2 is None:
                    limits = parse_partial_datetime(limit1, 'subset range date/time', parser)
                else:
                    limits = [parse_datetime(limit1, 'subset range start date/time', parser),
                              parse_datetime(limit2, 'subset range end date/time', parser)]
            elif dim_name.lower() in ['x', 'y', 'z']:
                limits = [parse_float(limit1, 'subset range start coordinate', parser),
                          parse_float(limit2, 'subset range start coordinate', parser)]
                if dim_name.lower() == 'x':
                    if not limits[0] <= limits[1]:
                        parser.error("Longitude limits must be monotonically increasing (i.e. for x[A,B] A <= B). For "
                                     "example, x=[90,-90] is invalid but x=[90,270] is valid")
                    if not limits[1] - limits[0] <= 360:
                        parser.error("Longitude limits should not be more than 360 degrees apart "
                                     "(i.e. for x[A,B] B-A <= 360)")
            else:
                limits = [parse_as_number_or_datetime(limit1), parse_as_number_or_datetime(limit2)]
            limit_dict[dim_name] = limits
    return limit_dict


def parse_colon_and_comma_separated_arguments(inputs, parser, options, compulsory_args):
    """
    :param inputs:    A list of strings, each in the format a:b:c:......:n where a,b,c,...,n are arguments
    :param parser:    The parser used to raise an error if one occurs
    :param options:   The possible options that each input can take. If no value is assigned to a particular option,
     then it is assigned None
    :param compulsory_args:   The exact number of compulsory arguments (colon separated)
    :return: A list of dictionaries containing the parsed arguments
    """
    # TODO I'm pretty sure this could be done by argparse more cleanly and efficiently, just pass it the split args...

    input_dicts = []
    for input_string in inputs:
        split_input = [re.sub(r'([\\]):', r':', word) for word in re.split(r'(?<!\\):', input_string)]
        if len(split_input) < compulsory_args:
            parser.error("A mandatory option is missing")
        elif len(split_input) > compulsory_args + 1:
            parser.error("Too many mandatory options")

        input_dict = {}

        option = list(options._asdict().keys())

        # First deal with the comma separated compulsory arguments
        for i in range(0, compulsory_args):
            try:
                current_option = split_input[i]
                input_dict[option[0]] = options[i](current_option, parser)
                option.pop(0)  # Compulsory arguments always the first in the list
            except IndexError:
                input_dict[option[i]] = None

        # Now deal with optional augments, if they exist. For each option loop through the list of arguments to see if
        # it exists, if so check and add to the dictionary.
        if len(split_input) == compulsory_args + 1:
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
            for j in split_input_comma:
                # Split the input, [0] will be the key and [1] the value in the list
                split_input_variable = split_outside_brackets(j, '=')
                if split_input_variable[0] == option:
                    input_dict[option] = options[i + compulsory_args](split_input_variable[1], parser)
                    split_input_comma.remove(j)

        if len(split_input_comma) != 0:
            raise InvalidCommandLineOptionError('The following optional arguments could not be parsed: ' +
                                                str(split_input_comma))

        input_dicts.append(input_dict)
    return input_dicts


def split_outside_brackets(input, seps=[','], brackets={'[': ']', '(': ')'}):
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
    from cis.utils import parse_key_val_list

    elements = multi_split(arguments, ['[', ',', ']'])
    method_name = elements[0] if len(elements) > 0 else ''
    args = elements[1:] if len(elements) > 1 else []
    method_and_args = (method_name, parse_key_val_list(args))
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
    """
    Checks plot type is valid option for number of variables if specified
    """

    if plot_type is not None:
        if plot_type not in plot_types.keys():
            parser.error(
                "'" + plot_type + "' is not a valid plot type, please use one of: " + str(plot_types.keys()))

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


def check_boolean(arg, parser):
    if arg is None or arg.lower() == "true":
        return True
    elif arg.lower() == "false":
        return False
    else:
        parser.error("'" + arg + "' is not either True or False")


def _split_output_if_includes_variable_name(arguments, parser):
    arguments.output_var = None
    if ':' in arguments.output:
        try:
            arguments.output_var, arguments.output = arguments.output.split(':')
        except ValueError:
            # Too many values to unpack
            parser.error("Invalid output path: should be a filename with one optional variable prefix.")


def _validate_output_file(arguments, parser, default_ext='.nc'):
    _split_output_if_includes_variable_name(arguments, parser)
    if not os.path.splitext(arguments.output)[1]:
        arguments.output += default_ext
    if _file_already_exists_and_no_overwrite(arguments):
        parser.exit(status=0, message="No operation performed")
    if _output_file_matches_an_input_file(arguments):
        parser.error("The input file must not be the same as the output file")


def _file_already_exists_and_no_overwrite(arguments):
    from six.moves import input
    # If the file already exists, and we haven't set the overwrite flag or env var, then prompt
    if os.path.isfile(arguments.output):
        overwrite_env = os.environ.get("CIS_FORCE_OVERWRITE", "").lower()
        if arguments.force_overwrite:
            return False
        elif overwrite_env:
            return overwrite_env == 'false'
        else:
            overwrite = None
            while overwrite not in ['y', 'n', '']:
                overwrite = input("The file: {} already exists. Overwrite? (y/[n])")
            if overwrite != 'y':
                return True
            # Otherwise False
    return False


def _output_file_matches_an_input_file(arguments):
    """
    Checks that the output file is not also one of the input files. Uses os.path.samefile where available (not NT) or
    falls back to comparing os.stat.
    :param arguments: The command line arguments
    :return: True if the output file is also an input file
    """
    match = False
    try:
        input_files = list(arguments.samplefiles)
    except AttributeError:
        input_files = []  # Only applies to collocation

    for datagroup in arguments.datagroups:
        input_files.extend(datagroup['filenames'])
    for input_file in input_files:
        if os.path.exists(arguments.output):
            # Windows doesn't have samefile support...
            if (hasattr(os.path, 'samefile') and os.path.samefile(arguments.output, input_file)) or \
                    (arguments.output == input_file and os.stat(arguments.output) == os.stat(input_file)):
                match = True
                break
    return match


def _create_attributes_dictionary(arguments, parser):
    """
    Convert the attributes string (of the form 'attr1=val1,attr2=val2') into a dictionary of key-value pairs
    """
    if arguments.attributes is not None:
        dict_pairs = arguments.attributes.split(',')
        attributes = {}
        for pair in dict_pairs:
            try:
                key, value = pair.split('=')
                if not (key and value):
                    raise ValueError
                attributes[key] = value
            except ValueError:
                parser.error("Invalid attribute: expected key-value pair in the format 'key=value', got '%s'" % pair)
        arguments.attributes = attributes


def validate_plot_args(arguments, parser):
    arguments.datagroups = get_plot_datagroups(arguments.datagroups, parser)

    if arguments.output is not None:
        _validate_output_file(arguments, parser, '.png')

    return arguments


def validate_info_args(arguments, parser):
    from collections import namedtuple
    # See how many colon-split arguments there are (taking into account escaped colons)
    split_input = [re.sub(r'([\\]):', r':', word) for word in re.split(r'(?<!\\):', arguments.datagroups[0])]
    if len(split_input) == 1:
        # If there is only one part of the datagroup then it must be a file (or list of files).
        DatagroupOptions = namedtuple('DatagroupOptions', ["filenames"])
        datagroup_options = DatagroupOptions(expand_file_list)
        arguments.datagroups = parse_colon_and_comma_separated_arguments(arguments.datagroups, parser,
                                                                         datagroup_options, compulsory_args=1)
    else:
        # Otherwise it's a standard datagroup
        arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    return arguments


def validate_col_args(arguments, parser):
    """
    Checks that the filenames are valid and that variables and methods have been specified.
    Assigns default method/variable to datagroups with unspecified method/variable if default is specified
    Checks that the product is valid if specified
    """
    # Note: Sample group is put into a list as parse_colonic_arguments expects a list.
    # Samplegroup will only ever be one argument though
    arguments.samplegroup = get_col_samplegroup([arguments.samplegroup], parser)

    # Take the three parts out of the 0th samplegroup.
    # Note: Due to the reason stated above, there will only ever be one samplegroup
    arguments.samplefiles = arguments.samplegroup["filenames"]
    arguments.samplevariable = arguments.samplegroup.get("variable", None)
    arguments.sampleproduct = arguments.samplegroup.get("product", None)
    arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    _validate_output_file(arguments, parser)

    return arguments


def validate_aggregate_args(arguments, parser):
    arguments.datagroups = get_aggregate_datagroups(arguments.datagroups, parser)
    arguments.grid = get_aggregate_grid(arguments.aggregategrid, parser)
    _validate_output_file(arguments, parser)
    return arguments


def validate_collapse_args(arguments, parser):
    arguments.datagroups = get_aggregate_datagroups(arguments.datagroups, parser)
    # If we only have one dimension just check if the user has comma separated the dims (as in aggregation)
    if len(arguments.dimensions) == 1:
        arguments.dimensions = arguments.dimensions[0].split(',')
    _validate_output_file(arguments, parser)
    return arguments


def validate_subset_args(arguments, parser):
    arguments.datagroups = get_basic_datagroups(arguments.datagroups, parser)
    arguments.limits = get_subset_limits(arguments.subsetranges, parser)
    _validate_output_file(arguments, parser)
    return arguments


def validate_eval_args(arguments, parser):
    arguments.datagroups = get_eval_datagroups(arguments.datagroups, parser)
    _create_attributes_dictionary(arguments, parser)
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
              'collocate': validate_col_args,
              'aggregate': validate_aggregate_args,
              'collapse': validate_collapse_args,
              'subset': validate_subset_args,
              'eval': validate_eval_args,
              'stats': validate_stats_args,
              'version': validate_version_args}

aliases = {'col': 'collocate',
           'sub': 'subset',
           'agg': 'aggregate'}


def parse_args(arguments=None):
    """
    Parse the arguments given. If no arguments are given, then used the command line arguments.
    Returns a dictionary contains the parsed arguments
    """
    parser = initialise_top_parser()
    if arguments is None:
        # sys.argv[0] is the name of the script itself
        arguments = sys.argv[1:]
    main_args = parser.parse_args(arguments)
    # TODO I don't really like this as I have to specify the aliases twice...
    if main_args.command in aliases.keys():
        main_args.command = aliases[main_args.command]

    # Firstly deal with logging verbosity - in case we log anything in the validation
    # The 'screen' handler is the first in the list
    if main_args.quiet:
        logging.getLogger().handlers[0].setLevel(logging.ERROR)
    elif main_args.verbose == 1:
        logging.getLogger().handlers[0].setLevel(logging.INFO)
    elif main_args.verbose == 2:
        logging.getLogger().handlers[0].setLevel(logging.DEBUG)

    main_args = validators[main_args.command](main_args, parser)

    return main_args
